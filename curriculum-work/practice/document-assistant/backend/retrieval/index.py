"""Small exact-search teaching index with transactional metadata and invalidation.

SQLite is trusted local storage, NOT an authentication service. Each nonempty
document line is a chunk; history/restricted records can be stored but are
filtered before ranking and checked again when preparing Context.
"""
import hashlib
import json
import math
from pathlib import Path
import re
import sqlite3
from collections import Counter

from retrieval.encoder import profile_hash


class ProfileMismatch(ValueError):
    pass


class StaleSelection(ValueError):
    pass


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def terms(text):
    # Eojeol/word baseline, not a Korean morphological analyzer or learned sparse model.
    return re.findall(r"[a-z0-9가-힣]+", text.lower())


def vector_ok(vector, dimension):
    if len(vector) != dimension or any(not math.isfinite(x) for x in vector):
        raise ValueError("Invalid vector dimension/number")
    if not math.isclose(sum(x*x for x in vector), 1.0, abs_tol=1e-4):
        raise ValueError("This index requires unit vectors")


def bm25_scores(query, texts, k1=1.5, b=0.75):
    docs = [Counter(terms(text)) for text in texts]
    n = len(docs)
    if not n:
        return []
    avg = sum(sum(d.values()) for d in docs)/n
    scores = [0.0]*n
    for word in sorted(set(terms(query))):
        df = sum(word in d for d in docs)
        idf = math.log(1 + (n-df+0.5)/(df+0.5))
        for i,d in enumerate(docs):
            tf=d[word]
            if tf:
                scores[i] += idf * tf*(k1+1)/(tf+k1*(1-b+b*sum(d.values())/max(avg,1)))
    return scores


class LocalIndex:
    def __init__(self, path, encoder):
        self.encoder=encoder
        self.db=sqlite3.connect(path)
        self.db.row_factory=sqlite3.Row
        try:
            row=self.db.execute("SELECT value FROM meta WHERE key='profile'").fetchone()
            if row is None or row[0] != json.dumps(encoder.profile,sort_keys=True):
                raise ProfileMismatch("Rebuild required, even when dimensions match")
        except Exception:
            self.db.close()
            raise

    @classmethod
    def create(cls,path,encoder,documents):
        path=Path(path)
        path.parent.mkdir(parents=True,exist_ok=True)
        path.touch(exist_ok=False)  # Never overwrite an earlier experiment.
        db=sqlite3.connect(path)
        try:
            db.executescript('''
                CREATE TABLE meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);
                CREATE TABLE documents(id TEXT PRIMARY KEY,version TEXT NOT NULL,
                    access TEXT NOT NULL,current INTEGER NOT NULL,deleted INTEGER NOT NULL,
                    title TEXT NOT NULL,text TEXT NOT NULL,content_sha TEXT NOT NULL);
                CREATE TABLE chunks(chunk_id TEXT PRIMARY KEY,doc_id TEXT NOT NULL,
                    line INTEGER NOT NULL,text TEXT NOT NULL,vector TEXT NOT NULL);
            ''')
            db.executemany("INSERT INTO meta VALUES(?,?)",[
                ("profile",json.dumps(encoder.profile,sort_keys=True)),("generation","0"),
                ("chunk_policy","nonempty_line_v1_no_overlap"),
                ("source","data/documents-v1.json")])
            db.commit()
        finally:
            db.close()
        index=cls(path,encoder)
        try:
            for document in documents:
                index.upsert(document)
            return index
        except Exception:
            index.close()
            raise

    def close(self):
        self.db.close()

    def check_profile(self):
        stored=self.db.execute("SELECT value FROM meta WHERE key='profile'").fetchone()[0]
        if stored!=json.dumps(self.encoder.profile,sort_keys=True):
            raise ProfileMismatch("Encoder configuration changed; rebuild required")

    @property
    def generation(self):
        return int(self.db.execute("SELECT value FROM meta WHERE key='generation'").fetchone()[0])

    def bump(self):
        self.db.execute("UPDATE meta SET value=CAST(value AS INTEGER)+1 WHERE key='generation'")

    def upsert(self, document):
        self.check_profile()
        if document['access'] not in ('staff','restricted') or type(document['current']) is not bool:
            raise ValueError("Unknown access/current metadata")
        if not all(isinstance(document[k],str) and document[k].strip() for k in ('id','version','title','text')):
            raise ValueError("Document strings are required")
        # Encode before transaction; a failure leaves previous content and vectors intact.
        lines=[(i,t) for i,t in enumerate(document['text'].splitlines(),1) if t.strip()]
        vectors=self.encoder.encode([document['title']+'\n'+t for _,t in lines],"passage")
        if len(vectors)!=len(lines):
            raise ValueError("Missing vectors")
        for vector in vectors:
            vector_ok(vector,self.encoder.profile['dimension'])
        with self.db:
            self.db.execute("DELETE FROM chunks WHERE doc_id=?",(document['id'],))
            self.db.execute("INSERT OR REPLACE INTO documents VALUES(?,?,?,?,?,?,?,?)",(
                document['id'],document['version'],document['access'],int(document['current']),0,
                document['title'],document['text'],sha(document['text'])))
            self.db.executemany("INSERT INTO chunks VALUES(?,?,?,?,?)",[
                (f"{document['id']}@{document['version']}:L{line}",document['id'],line,text,json.dumps(vector))
                for (line,text),vector in zip(lines,vectors)])
            self.bump()

    def delete(self, doc_id):
        with self.db:
            if self.db.execute("SELECT 1 FROM documents WHERE id=?",(doc_id,)).fetchone() is None:
                raise ValueError("Unknown document")
            self.db.execute("DELETE FROM chunks WHERE doc_id=?",(doc_id,))
            # Tombstone retains ID/version only; source body and title are removed here.
            self.db.execute("UPDATE documents SET deleted=1,text='',title='',content_sha='' WHERE id=?",(doc_id,))
            self.bump()

    def search(self, question, *, method='dense', k=3, manifest_ids=None):
        self.check_profile()
        if not isinstance(question,str) or not question.strip() or len(question)>2000:
            raise ValueError("Question must be 1..2000 nonblank characters")
        if method not in ('dense','bm25','hybrid') or type(k) is not int or not 1<=k<=10:
            raise ValueError("Unknown method or k")
        generation=self.generation
        # Fixed trusted teaching role. The query text cannot supply access/current flags.
        rows=[dict(r) for r in self.db.execute('''SELECT c.*,d.version,d.content_sha,d.title
            FROM chunks c JOIN documents d ON c.doc_id=d.id
            WHERE d.access='staff' AND d.current=1 AND d.deleted=0 ORDER BY c.chunk_id''')]
        if manifest_ids is not None:
            rows=[r for r in rows if r['doc_id'] in manifest_ids]
        lexical=bm25_scores(question,[r['title']+'\n'+r['text'] for r in rows])
        dense=[]
        if method in ('dense','hybrid') and rows:
            vector=self.encoder.encode([question.strip()],"query")[0]
            vector_ok(vector,self.encoder.profile['dimension'])
            for row in rows:
                stored=json.loads(row['vector']);vector_ok(stored,len(vector))
                dense.append(sum(a*b for a,b in zip(vector,stored)))
        def ranked(scores,positive=False):
            return sorted([i for i,s in enumerate(scores) if not positive or s>0],
                          key=lambda i:(-scores[i],rows[i]['chunk_id']))
        if method=='bm25':
            order=ranked(lexical,True);scores=lexical
        elif method=='dense':
            order=ranked(dense);scores=dense
        else:
            # RRF combines ranks, not incompatible raw BM25/cosine scores.
            scores=[0.0]*len(rows)
            for order_ in (ranked(dense),ranked(lexical,True)):
                for rank,i in enumerate(order_,1): scores[i]+=1/(60+rank)
            order=ranked(scores,True)
        hits=[]
        for i in order[:k]:
            row=rows[i]
            hits.append({key:row[key] for key in ('chunk_id','doc_id','version','line','text','content_sha')}
                |dict(score=round(scores[i],8),origin_path='data/documents-v1.json',
                      source_locator=f"sqlite:documents/{row['doc_id']}@{row['version']}:L{row['line']}"))
        return dict(method=method,k=k,query_sha256=sha(question.strip()),generation=generation,
            profile_sha256=profile_hash(self.encoder.profile),eligible_chunks=len(rows),hits=hits,
            actor='staff_teaching_fixture_not_authentication')

    def context(self, selection):
        self.check_profile()
        # Reject stale snapshots; callers must search again after ANY index mutation.
        if selection['generation']!=self.generation or selection['profile_sha256']!=profile_hash(self.encoder.profile):
            raise StaleSelection("Index changed; search again before Context assembly")
        result=[]
        for hit in selection['hits']:
            row=self.db.execute('''SELECT c.*,d.version,d.content_sha,d.access,d.current,d.deleted
                FROM chunks c JOIN documents d ON c.doc_id=d.id WHERE c.chunk_id=?''',(hit['chunk_id'],)).fetchone()
            if row is None or row['access']!='staff' or not row['current'] or row['deleted'] or row['content_sha']!=hit['content_sha']:
                raise StaleSelection("Source no longer eligible")
            # Never trust the text of an earlier result supplied by the caller.
            result.append(dict(doc_id=row['doc_id'],version=row['version'],line=row['line'],
                               text=row['text'],origin_path='data/documents-v1.json',
                               source_locator=f"sqlite:documents/{row['doc_id']}@{row['version']}:L{row['line']}"))
        return result

    def manifest(self):
        self.check_profile()
        return dict(profile=self.encoder.profile,profile_sha256=profile_hash(self.encoder.profile),
            generation=self.generation,chunk_policy='nonempty_line_v1_no_overlap',
            documents=[dict(r) for r in self.db.execute('SELECT id,version,access,current,deleted,content_sha FROM documents ORDER BY id')],
            total_chunks=self.db.execute('SELECT COUNT(*) FROM chunks').fetchone()[0])
