"""Claim-bound local review ledger. Trusted CLI fixture, not reviewer authentication.

Software validates identity/quotation/currentness, NOT semantic entailment.
Review rows are not document approval; Registry review state remains distinct.
"""
import hashlib
import json

TEMPLATE = "kedu-evidence-report-v1"


class ReportRejected(ValueError):
    pass


def stable(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def fingerprint(value):
    return hashlib.sha256(stable(value).encode()).hexdigest()


class Reports:
    def __init__(self, registry):
        self.registry = registry
        self.db = registry.db
        self.db.execute('''CREATE TABLE IF NOT EXISTS report_reviews(
          binding TEXT PRIMARY KEY,decision TEXT,reviewer TEXT,reason TEXT)''')
        self.db.commit()

    def prepare(self, title, claims):
        if not isinstance(title, str) or not title.strip() or len(title)>100:
            raise ReportRejected("Title required, up to 100 characters")
        if not isinstance(claims,list) or not 1<=len(claims)<=8:
            raise ReportRejected("1..8 claims required")
        ids=set(); result=[]
        for claim in claims:
            if set(claim)!={'id','statement','citations'}: raise ReportRejected("Unknown claim fields")
            id=claim['id'];statement=claim['statement']
            if not isinstance(id,str) or not id or len(id)>30 or id in ids: raise ReportRejected("Duplicate/invalid claim ID")
            ids.add(id)
            if not isinstance(statement,str) or not statement.strip() or len(statement)>500: raise ReportRejected("Claim text required, up to 500 characters")
            citations=claim['citations']
            if not isinstance(citations,list) or not 1<=len(citations)<=3: raise ReportRejected("1..3 citations per claim required")
            sources=[]
            for citation in citations:
                if set(citation)!={'doc','version','element','quote'}: raise ReportRejected("Unknown citation fields")
                if type(citation['version']) is not int: raise ReportRejected("Internal version must be integer")
                row=self.registry.eligible(citation['doc'],citation['version'])
                if row['state']!='review': raise ReportRejected("Source must be in review state")
                if hashlib.sha256(row['source']).hexdigest()!=row['sha']: raise ReportRejected("Stored source hash mismatch")
                ir=json.loads(row['ir'])
                if ir['source_sha256']!=row['sha']: raise ReportRejected("IR source mismatch")
                element=next((e for e in ir['elements'] if e['id']==citation['element']),None)
                quote=citation['quote']
                if not element or not isinstance(quote,str) or not quote.strip() or len(quote)>500 or quote not in element['text']:
                    raise ReportRejected("Unknown element or quotation mismatch")
                sources.append(dict(doc=row['id'],version=row['version'],title=row['title'],source_sha256=row['sha'],parser=ir['parser'],element=element['id'],locator=element['locator'],quote=quote))
            result.append(dict(id=id,statement=statement,citations=sources))
        return dict(schema='l9-document-spec-v1',template=TEMPLATE,title=title,
            generation=self.registry.generation,claims=result,
            semantic_validation='requires_reviewer; citation presence is not entailment',
            review_mode='trusted_local_fixture_not_authenticated_human')

    def check_current(self,spec):
        raw=[dict(id=c['id'],statement=c['statement'],citations=[{k:s[k] for k in ('doc','version','element','quote')} for s in c['citations']]) for c in spec['claims']]
        current=self.prepare(spec['title'],raw)
        if stable(current)!=stable(spec): raise ReportRejected("Spec/source/template/generation changed; review again")

    def decide(self,spec,decision,reviewer,reason):
        self.check_current(spec)
        if decision not in ('approve','reject') or not isinstance(reviewer,str) or not reviewer.strip() or not isinstance(reason,str) or not reason.strip():
            raise ReportRejected("Decision, reviewer and reason required")
        with self.db:
            self.db.execute("INSERT INTO report_reviews VALUES(?,?,?,?)",(fingerprint(spec),decision,reviewer,reason))
        return fingerprint(spec)

    def authorized(self,spec):
        self.check_current(spec)
        row=self.db.execute("SELECT * FROM report_reviews WHERE binding=?",(fingerprint(spec),)).fetchone()
        if not row or row['decision']!='approve': raise ReportRejected("Matching approved review required")
        return dict(row)
