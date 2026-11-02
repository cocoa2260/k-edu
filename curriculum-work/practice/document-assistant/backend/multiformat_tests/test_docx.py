import io
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from app.docx_ingest import DocxRejected,read_docx,W
from app.document_registry import Registry,parse_bytes
from app.report_spec import Reports,ReportRejected
from tools.report_export import format_location

SOURCE=Path('data/multiformat-v1/policy.docx')


def changed(replacements=None,extra=None):
    replacements=replacements or {};out=io.BytesIO()
    with zipfile.ZipFile(SOURCE) as original,zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED) as target:
        for item in original.infolist():
            data=original.read(item.filename)
            if item.filename in replacements:data=replacements[item.filename](data)
            target.writestr(item.filename,data)
        for name,value in (extra or {}).items():target.writestr(name,value)
    return out.getvalue()


class DocxTests(unittest.TestCase):
    def test_actual_docx_paragraph_and_table(self):
        elements=read_docx(SOURCE.read_bytes());gold=json.loads(Path('data/multiformat-v1/gold.json').read_text())
        self.assertIn(gold['docx_paragraph'],[e['text'] for e in elements]);table=next(e for e in elements if e['kind']=='table');self.assertEqual(table['rows'],gold['docx_table']);self.assertEqual(table['header_rows'],[1])
    def test_cell_is_structural_not_pdf_page(self):
        cell=next(e for e in read_docx(SOURCE.read_bytes()) if e['kind']=='table_cell' and e['text']=='15000원');self.assertEqual(cell['locator']['row'],3);self.assertEqual(cell['locator']['column'],3);self.assertNotIn('page',cell['locator']);self.assertIn('행 3 열 3',format_location(cell['locator']))
    def test_body_order_and_table_reference(self):
        elements=read_docx(SOURCE.read_bytes());self.assertTrue(elements[0]['text'].startswith('환불'));table=next(e for e in elements if e['kind']=='table');self.assertEqual(sum(e.get('table_id')==table['id'] for e in elements),9)
    def test_not_zip(self):
        with self.assertRaises(DocxRejected):read_docx(b'not a document')
    def test_empty_package(self):
        b=io.BytesIO()
        with zipfile.ZipFile(b,'w'):pass
        with self.assertRaises(DocxRejected):read_docx(b.getvalue())
    def test_bad_content_type(self):
        data=changed({'[Content_Types].xml':lambda b:b.replace(b'wordprocessingml.document.main+xml',b'wrong-format')})
        with self.assertRaises(DocxRejected):read_docx(data)
    def test_bad_main_relationship(self):
        with self.assertRaises(DocxRejected):read_docx(changed({'_rels/.rels':lambda b:b.replace(b'Target="word/document.xml"',b'Target="wrong.xml"')}))
    def test_external_relationship(self):
        with self.assertRaises(DocxRejected):read_docx(changed(extra={'_rels/extra.rels':b'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship TargetMode="External" Target="https://example.com"/></Relationships>'}))
    def test_unsafe_member(self):
        for name in ('../outside.xml','/absolute.xml','word\\outside.xml'):
            with self.subTest(name=name),self.assertRaises(DocxRejected):read_docx(changed(extra={name:b'x'}))
    def test_extra_visible_parts(self):
        for name in ('word/header1.xml','word/footnotes.xml','word/media/image.png','word/comments.xml','word/vbaProject.bin'):
            with self.subTest(name=name),self.assertRaises(DocxRejected):read_docx(changed(extra={name:b'fixture'}))
    def test_unsupported_content_is_not_silently_dropped(self):
        for element in ('ins','del','drawing','fldSimple','sdt','hyperlink'):
            replacement=b'<w:p><w:'+element.encode()+b'/>'
            data=changed({'word/document.xml':lambda b:b.replace(b'<w:p>',replacement,1)})
            with self.subTest(element=element),self.assertRaisesRegex(DocxRejected,'Unsupported'):read_docx(data)
    def test_merged_cells_rejected(self):
        with self.assertRaises(DocxRejected):read_docx(changed({'word/document.xml':lambda b:b.replace(b'<w:tcPr>',b'<w:tcPr><w:gridSpan w:val="2"/>',1)}))
    def test_nested_table_rejected(self):
        with self.assertRaises(DocxRejected):read_docx(changed({'word/document.xml':lambda b:b.replace(b'</w:tcPr>',b'</w:tcPr><w:tbl/>',1)}))
    def test_malformed_xml(self):
        with self.assertRaises(DocxRejected):read_docx(changed({'word/document.xml':lambda b:b'<broken'}))
    def test_dtd_rejected(self):
        with self.assertRaises(DocxRejected):read_docx(changed({'word/document.xml':lambda b:b'<!DOCTYPE doc [<!ENTITY secret "x">]>'+b[b.index(b'<w:document'):]}))
    def test_compression_expansion_limit(self):
        with self.assertRaises(DocxRejected):read_docx(changed(extra={'huge.bin':b'x'*1_000_000}))
    def test_entry_count_limit(self):
        with self.assertRaises(DocxRejected):read_docx(changed(extra={f'x/{n}':b'x' for n in range(257)}))
    def test_input_byte_limit(self):
        with self.assertRaises(DocxRejected):read_docx(b'x'*8_000_001)
    def test_permission_precedes_docx_parsing(self):
        from app.document_ingest import DocumentRejected
        with self.assertRaises(DocumentRejected):parse_bytes(b'bad','docx',dict(id='x',version='1',title='x',access='restricted',current=True))
    def test_registry_cell_citation_and_invalidation(self):
        with tempfile.TemporaryDirectory() as folder:
            r=Registry(Path(folder)/'db')
            try:
                metadata=dict(id='docx',version='external-v1',title='가상 문서',access='staff',current=True)
                r.upload(SOURCE,metadata,'first');r.parse('docx',1);r.index('docx',1);r.review('docx',1)
                row=next(row for row in r.context(r.search('15000원')) if row['element']['kind']=='table_cell')
                reports=Reports(r);spec=reports.prepare('표 근거 시연',[dict(id='C1',statement='합성 표의 부담금 문자열을 확인한다.',citations=[dict(doc='docx',version=1,element=row['element']['id'],quote='15000원')])]);reports.decide(spec,'approve','fixture','같은 세션 시연')
                self.assertEqual(reports.authorized(spec)['decision'],'approve');r.delete('docx',1)
                with self.assertRaises(ValueError):reports.authorized(spec)
            finally:r.close()
    def test_duplicate_member_rejected(self):
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter('ignore',UserWarning);data=changed(extra={'word/document.xml':b'<duplicate/>'})
        with self.assertRaisesRegex(DocxRejected,'duplicate'):read_docx(data)
    def test_inherited_numbering_not_silently_omitted(self):
        with self.assertRaisesRegex(DocxRejected,'inherited'):
            read_docx(changed({'word/document.xml':lambda b:b.replace(b'w:val="Title"',b'w:val="ListNumber"',1)}))
    def test_false_table_header_not_promoted(self):
        data=changed({'word/document.xml':lambda b:b.replace(b'<w:tblHeader/>',b'<w:tblHeader w:val="0"/>')})
        self.assertEqual(next(e for e in read_docx(data) if e['kind']=='table')['header_rows'],[])


if __name__=='__main__':unittest.main()
