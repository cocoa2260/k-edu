"""One DocumentSpec -> DOCX/PDF. Local gate checked before and after staging.

Not an atomic publication service across filesystem/DB or concurrent workers.
"""
from pathlib import Path
import os
import tempfile
from xml.sax.saxutils import escape

from app.report_spec import fingerprint


def format_location(locator):
    if locator['kind']=='pdf_region':return '물리 페이지 '+str(locator['page'])+' 영역 '+', '.join(f'{x:.2f}' for x in locator['bbox'])+' point'
    if locator['kind']=='text_line':return '원본 줄 '+str(locator['line'])
    if locator['kind']=='docx_paragraph':return 'DOCX 본문 블록 '+str(locator['body_block'])+' 문단'
    if locator['kind']=='docx_cell':return 'DOCX 표 '+str(locator['table'])+' 행 '+str(locator['row'])+' 열 '+str(locator['column'])
    raise ValueError('Unsupported citation locator')


def paragraphs(spec):
    yield '합성 문서 근거 검토 시연'
    yield spec['title']
    yield '교육용 가상 자료입니다. 아래 검토 결정은 로컬 고정 검토자 시연이며 독립적인 업무 승인이나 정책 판단이 아닙니다.'
    for claim in spec['claims']:
        yield claim['id']+' 검토할 주장'
        yield claim['statement']
        for n,source in enumerate(claim['citations'],1):
            yield '근거 '+str(n)+' '+source['quote']
            locator=source['locator']
            position=format_location(locator)
            yield source['doc']+' 내부 버전 '+str(source['version'])+' '+position
            yield '원본 SHA256 '+source['source_sha256']
    yield '검토와 출력의 범위'
    yield '출처의 현재 버전과 인용 문자열을 검사했습니다. 주장과 근거의 의미 일치, 누락 조건, 독립 검토와 실제 서비스 인증은 별도 확인해야 합니다.'
    yield 'DocumentSpec SHA256 '+fingerprint(spec)


def write_docx(spec,path):
    from docx import Document
    from docx.shared import Inches,Pt,RGBColor
    from docx.oxml.ns import qn
    doc=Document();sec=doc.sections[0]
    sec.page_width=Inches(8.5);sec.page_height=Inches(11)
    sec.top_margin=sec.bottom_margin=Inches(.7)
    sec.left_margin=sec.right_margin=Inches(.75)
    for name in ('Normal','Title','Heading 1','Heading 2'):
        s=doc.styles[name];s.font.name='Noto Sans KR';s.font.color.rgb=RGBColor(0,0,0)
        s.element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'),'Noto Sans KR')
        s.paragraph_format.space_after=Pt(7)
    # Strip theme font/border residue from Word's built-in template.
    for border in list(doc.styles.element.iter(qn('w:pBdr'))):
        border.getparent().remove(border)
    doc.styles['Normal'].font.size=Pt(11)
    doc.styles['Title'].font.size=Pt(21)
    doc.styles['Heading 1'].font.size=Pt(14)
    # Explicit readable leading prevents font metrics from doubling line height.
    for name in ('Normal','Title','Heading 1','Heading 2'):
        style=doc.styles[name]
        style.paragraph_format.line_spacing=Pt(26 if name=='Title' else 20 if name.startswith('Heading') else 16)
        style.paragraph_format.space_before=Pt(9 if name.startswith('Heading') else 0)
        style.paragraph_format.space_after=Pt(6)
    for n,text in enumerate(paragraphs(spec)):
        if n==0:doc.add_paragraph(text,'Title')
        elif n==1 or text.endswith('검토할 주장') or text=='검토와 출력의 범위':doc.add_paragraph(text,'Heading 1')
        else:
            p=doc.add_paragraph(text)
            if 'SHA256 ' in text:
                for run in p.runs:run.font.size=Pt(8)
    for paragraph in doc.paragraphs:
        for run in paragraph.runs:
            run.font.name='Noto Sans KR';run.font.color.rgb=RGBColor(0,0,0)
            fonts=run._element.get_or_add_rPr().rFonts
            for key in list(fonts.attrib):
                if key.endswith('Theme'):del fonts.attrib[key]
            for script in ('ascii','hAnsi','eastAsia','cs'):fonts.set(qn('w:'+script),'Noto Sans KR')
    doc.core_properties.author='K-Edu synthetic teaching lab'
    doc.save(path)


def write_pdf(spec,path,font):
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.pagesizes import letter
    pdfmetrics.registerFont(TTFont('KeduKR',str(font)))
    body=ParagraphStyle('body',fontName='KeduKR',fontSize=11,leading=17,spaceAfter=8,wordWrap='CJK')
    heading=ParagraphStyle('heading',parent=body,fontSize=14,leading=20,spaceBefore=8,keepWithNext=True)
    title=ParagraphStyle('title',parent=body,fontSize=21,leading=28,spaceAfter=14)
    small=ParagraphStyle('hash',parent=body,fontSize=8,leading=12)
    story=[]
    for n,text in enumerate(paragraphs(spec)):
        style=title if n==0 else heading if n==1 or text.endswith('검토할 주장') or text=='검토와 출력의 범위' else small if 'SHA256 ' in text else body
        story.append(Paragraph(escape(text),style))
    def footer(canvas,doc):
        canvas.setFont('KeduKR',9);canvas.drawString(54,26,'K-Edu 합성 검토 시연');canvas.drawRightString(558,26,str(doc.page))
    SimpleDocTemplate(str(path),pagesize=letter,rightMargin=54,leftMargin=54,topMargin=50,bottomMargin=48).build(story,onFirstPage=footer,onLaterPages=footer)


def export(reports,spec,output,font,*,after_stage=None):
    review=reports.authorized(spec)
    output=Path(output)
    if output.exists():raise FileExistsError('New output directory required')
    output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='l9-report-',dir=output.parent) as folder:
        staging=Path(folder)/'result';staging.mkdir()
        write_docx(spec,staging/'evidence-report.docx')
        write_pdf(spec,staging/'evidence-report.pdf',font)
        if after_stage:after_stage()
        reports.authorized(spec)
        import json
        (staging/'document-spec.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n')
        (staging/'review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
        os.rename(staging,output)
    return output
