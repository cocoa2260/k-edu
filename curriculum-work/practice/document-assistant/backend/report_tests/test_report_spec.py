import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from app.document_registry import Registry,RegistryError
from app.report_spec import Reports,ReportRejected
from tools.report_export import export


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.path=self.root/'policy.txt';self.path.write_text('신청 기한 7일\n금액 15000원',encoding='utf-8')
        self.r=Registry(self.root/'db.sqlite');self.meta=dict(id='policy',version='external-1',access='staff',current=True,title='가상 정책')
        self.r.upload(self.path,self.meta,'one');self.r.parse('policy',1);self.r.index('policy',1);self.r.review('policy',1)
        self.reports=Reports(self.r)
        self.claims=[dict(id='C1',statement='신청 기한 7일',citations=[dict(doc='policy',version=1,element='line-1',quote='신청 기한 7일')])]
    def tearDown(self):self.r.close();self.tmp.cleanup()
    def spec(self):return self.reports.prepare('합성 정책 검토',self.claims)
    def approve(self,s):self.reports.decide(s,'approve','fixture-reviewer','같은 세션의 고정 시연')
    def test_binding_and_canonical_locator(self):
        s=self.spec();self.approve(s);self.assertEqual(self.reports.authorized(s)['decision'],'approve');self.assertEqual(s['claims'][0]['citations'][0]['locator']['line'],1)
    def test_pending_blocks_export(self):
        with self.assertRaises(ReportRejected):export(self.reports,self.spec(),self.root/'out','unused')
        self.assertFalse((self.root/'out').exists())
    def test_rejection_blocks(self):
        s=self.spec();self.reports.decide(s,'reject','fixture','조건 미확인')
        with self.assertRaises(ReportRejected):self.reports.authorized(s)
    def test_modified_claim_invalidates_review(self):
        s=self.spec();self.approve(s);s['claims'][0]['statement']='신청 기한 30일'
        with self.assertRaises(ReportRejected):self.reports.authorized(s)
    def test_template_change_requires_review(self):
        s=self.spec();self.approve(s);s['template']='unapproved'
        with self.assertRaises(ReportRejected):self.reports.authorized(s)
    def test_locator_tampering_refused(self):
        s=self.spec();self.approve(s);s['claims'][0]['citations'][0]['locator']['line']=999
        with self.assertRaises(ReportRejected):self.reports.authorized(s)
    def test_quote_mismatch(self):
        self.claims[0]['citations'][0]['quote']='30일'
        with self.assertRaises(ReportRejected):self.spec()
    def test_unknown_element(self):
        self.claims[0]['citations'][0]['element']='unknown'
        with self.assertRaises(ReportRejected):self.spec()
    def test_no_citation(self):
        self.claims[0]['citations']=[]
        with self.assertRaises(ReportRejected):self.spec()
    def test_duplicate_claim_ids(self):
        self.claims*=2
        with self.assertRaises(ReportRejected):self.spec()
    def test_version_change(self):
        s=self.spec();self.approve(s);self.r.upload(self.path,self.meta,'two')
        with self.assertRaises(RegistryError):self.reports.authorized(s)
    def test_restricted_source(self):
        s=self.spec();self.approve(s);self.r.restrict('policy',1)
        with self.assertRaises(RegistryError):self.reports.authorized(s)
    def test_deleted_source(self):
        s=self.spec();self.approve(s);self.r.delete('policy',1)
        with self.assertRaises(RegistryError):self.reports.authorized(s)
    def test_reindex_requires_review_state_again(self):
        s=self.spec();self.approve(s);self.r.index('policy',1)
        with self.assertRaises(ReportRejected):self.reports.authorized(s)
    def test_source_blob_corruption(self):
        s=self.spec();self.approve(s)
        with self.r.db:self.r.db.execute("UPDATE docs SET source=?",(b'corrupted',))
        with self.assertRaises(ReportRejected):self.reports.authorized(s)
    def test_semantic_entailment_is_not_automatic(self):
        self.claims[0]['statement']='신청 기한은 30일이다'
        s=self.spec() # matching 7-day quote can exist while statement is wrong
        self.reports.decide(s,'reject','fixture','7일 근거가 30일 주장을 지지하지 않음')
        with self.assertRaises(ReportRejected):self.reports.authorized(s)
    def test_mid_stage_delete_no_output(self):
        s=self.spec();self.approve(s)
        with patch('tools.report_export.write_docx'),patch('tools.report_export.write_pdf'):
            with self.assertRaises(RegistryError):export(self.reports,s,self.root/'out','unused',after_stage=lambda:self.r.delete('policy',1))
        self.assertFalse((self.root/'out').exists())
    def test_render_failure_no_output(self):
        s=self.spec();self.approve(s)
        with patch('tools.report_export.write_docx',side_effect=RuntimeError('render fixture')):
            with self.assertRaises(RuntimeError):export(self.reports,s,self.root/'out','unused')
        self.assertFalse((self.root/'out').exists())
    def test_claim_budget(self):
        self.claims*=9
        with self.assertRaises(ReportRejected):self.spec()
    def test_review_persists_after_reopen(self):
        s=self.spec();self.approve(s);self.r.close();self.r=Registry(self.root/'db.sqlite');self.reports=Reports(self.r)
        self.assertEqual(self.reports.authorized(s)['decision'],'approve')


if __name__=='__main__':unittest.main()
