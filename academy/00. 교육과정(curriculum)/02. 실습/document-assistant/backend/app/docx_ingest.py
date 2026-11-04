"""Bounded, deliberately narrow DOCX reader, not a general Office renderer.

Supports simple main-body paragraphs and rectangular unmerged tables only.
Structural locators do not claim Word pagination. Does not extract ZIP paths.
"""
import io
from pathlib import PurePosixPath
import re
import xml.etree.ElementTree as ET
import zipfile

W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
CONTENT='http://schemas.openxmlformats.org/package/2006/content-types'
REL='http://schemas.openxmlformats.org/package/2006/relationships'
OFFICE_REL='http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument'
MAIN_TYPE='application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml'
PARSER='l9-docx-simple-v1'


class DocxRejected(ValueError):
    pass


def tag(name):return '{'+W+'}'+name


def xml(data):
    if len(data)>4_000_000:raise DocxRejected('XML size limit')
    try:
        text=data.decode('utf-8-sig')
        if '\x00' in text or re.search(r'<!\s*(DOCTYPE|ENTITY)',text,re.I):raise DocxRejected('DTD/entity/non-UTF8 XML unsupported')
        return ET.fromstring(text)
    except (UnicodeError,ET.ParseError) as error:raise DocxRejected('Invalid XML') from error


def children(node,allowed):
    if any(child.tag not in {tag(n) for n in allowed} for child in node):raise DocxRejected('Unsupported content element')


def paragraph(node):
    children(node,{'pPr','r'})
    result=[]
    for run in node.findall(tag('r')):
        children(run,{'rPr','t','tab','br'})
        for part in run:
            if part.tag==tag('t'):result.append(part.text or '')
            elif part.tag==tag('tab'):result.append('\t')
            elif part.tag==tag('br'):
                if part.get(tag('type'),'textWrapping')!='textWrapping':raise DocxRejected('Page/column break unsupported')
                result.append('\n')
    return ''.join(result)


def read_docx(data):
    if len(data)>8_000_000:raise DocxRejected('DOCX byte limit')
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            info=archive.infolist();names=[i.filename for i in info]
            if not info or len(info)>256 or len(set(names))!=len(names):raise DocxRejected('ZIP entry count/duplicate names')
            if sum(i.file_size for i in info)>16_000_000:raise DocxRejected('Expanded ZIP limit')
            for item in info:
                path=PurePosixPath(item.filename)
                if path.is_absolute() or '..' in path.parts or '\\' in item.filename or item.flag_bits&1:raise DocxRejected('Unsafe/encrypted ZIP member')
                if item.file_size>4_000_000 or item.file_size>200*max(1,item.compress_size):raise DocxRejected('ZIP member size/ratio limit')
                if item.filename.lower().startswith(('word/header','word/footer','word/footnotes','word/endnotes','word/comments','word/vba','word/embeddings','word/media')):raise DocxRejected('Unsupported Office part')
            required={'[Content_Types].xml','_rels/.rels','word/document.xml'}
            if not required.issubset(names):raise DocxRejected('Not a supported DOCX package')
            types=xml(archive.read('[Content_Types].xml'))
            if not any(e.tag=='{'+CONTENT+'}Override' and e.get('PartName')=='/word/document.xml' and e.get('ContentType')==MAIN_TYPE for e in types):raise DocxRejected('DOCX main content type mismatch')
            rels=xml(archive.read('_rels/.rels'))
            if not any(e.get('Type')==OFFICE_REL and e.get('Target')=='word/document.xml' for e in rels):raise DocxRejected('Main relationship mismatch')
            for name in names:
                if name.endswith('.rels'):
                    rel=xml(archive.read(name))
                    if rel.tag!='{'+REL+'}Relationships' or any(e.get('TargetMode')=='External' for e in rel):raise DocxRejected('External relationship unsupported')
            root=xml(archive.read('word/document.xml'))
            styles=xml(archive.read('word/styles.xml')) if 'word/styles.xml' in names else None
    except (zipfile.BadZipFile,KeyError,RuntimeError,NotImplementedError) as error:raise DocxRejected('Unreadable DOCX package') from error
    if root.tag!=tag('document'):raise DocxRejected('Wrong main XML root')
    body=root.find(tag('body'))
    if body is None:raise DocxRejected('Missing body')
    # Formatting properties can contain visible numbering/hidden text too.
    forbidden={'ins','del','moveFrom','moveTo','drawing','pict','object','fldSimple','instrText','hyperlink','sdt','altChunk','footnoteReference','endnoteReference','commentReference','headerReference','footerReference','numPr','vanish','webHidden','gridSpan','vMerge','hMerge','gridBefore','gridAfter'}
    if any(node.tag in {tag(n) for n in forbidden} for node in root.iter()):raise DocxRejected('Unsupported visible/hidden content or merged cells')
    # A paragraph can inherit hidden text or numbering through an applied style.
    style_map={} if styles is None else {s.get(tag('styleId')):s for s in styles.findall(tag('style'))}
    if styles is not None:
        defaults=styles.find(tag('docDefaults'))
        if defaults is not None and any(n.tag in {tag('vanish'),tag('webHidden'),tag('numPr')} for n in defaults.iter()):raise DocxRejected('Unsupported default visibility/numbering')
    applied=[n.get(tag('val')) for n in root.iter() if n.tag in (tag('pStyle'),tag('rStyle'))]
    applied.extend(s.get(tag('styleId')) for s in style_map.values() if s.get(tag('default'))=='1')
    for name in applied:
        seen=set()
        while name:
            if name in seen or name not in style_map:raise DocxRejected('Unknown/cyclic applied style')
            seen.add(name);style=style_map[name]
            if any(n.tag in {tag('numPr'),tag('vanish'),tag('webHidden')} for n in style.iter()):raise DocxRejected('Unsupported inherited visibility/numbering')
            parent=style.find(tag('basedOn'));name=parent.get(tag('val')) if parent is not None else None
    children(body,{'p','tbl','sectPr'})
    elements=[];table_number=0
    for block_number,block in enumerate(body,1):
        locator=dict(part='word/document.xml',body_block=block_number)
        if block.tag==tag('p'):
            text=paragraph(block)
            if text.strip():elements.append(dict(id=f'docx-b{block_number}',kind='paragraph',text=text,locator=dict(locator,kind='docx_paragraph')))
        elif block.tag==tag('tbl'):
            table_number+=1;children(block,{'tblPr','tblGrid','tr'});rows=[];cells=[];headers=[]
            grid=block.find(tag('tblGrid'));columns=0 if grid is None else len(grid.findall(tag('gridCol')))
            if not 1<=columns<=20:raise DocxRejected('Unsupported table grid')
            for row_number,row in enumerate(block.findall(tag('tr')),1):
                children(row,{'trPr','tc'});parts=row.findall(tag('tc'))
                if len(parts)!=columns or row_number>100:raise DocxRejected('Nonrectangular/oversized table')
                values=[]
                header=row.find(tag('trPr')+'/'+tag('tblHeader'))
                if header is not None and header.get(tag('val'),'true') not in ('0','false','off'):headers.append(row_number)
                for col_number,cell in enumerate(parts,1):
                    children(cell,{'tcPr','p'})
                    text='\n'.join(paragraph(p) for p in cell.findall(tag('p')));values.append(text)
                    if text.strip():cells.append(dict(id=f'docx-b{block_number}-r{row_number}-c{col_number}',kind='table_cell',text=text,table_id=f'docx-b{block_number}-table',locator=dict(locator,kind='docx_cell',table=table_number,row=row_number,column=col_number)))
                rows.append(values)
            if not rows:raise DocxRejected('Empty table')
            elements.append(dict(id=f'docx-b{block_number}-table',kind='table',text='',rows=rows,header_rows=headers,locator=dict(locator,kind='docx_table',table=table_number)))
            elements.extend(cells)
    if not elements or len(elements)>1000 or sum(len(e['text']) for e in elements)>200000:raise DocxRejected('Empty/oversized document')
    return elements
