"""L9 local intake/IR lifecycle laboratory. Trusted staff CLI, not authentication.

No vectors or web upload. SQLite keyword search demonstrates lifecycle filtering.
Original bytes retained until explicit delete; backups/external copies are out of scope.
"""
import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile

from app.document_ingest import authorize, ingest


class RegistryError(ValueError):
    pass


def digest(data):
    return hashlib.sha256(data).hexdigest()


def parse_bytes(data, fmt, metadata):
    authorize(metadata)
    if fmt == "txt":
        text = data.decode("utf-8-sig")
        if "\x00" in text: raise RegistryError("Binary text unsupported")
        elements = [dict(id=f"line-{n}",kind="paragraph",text=t,
            locator=dict(kind="text_line",line=n)) for n,t in enumerate(text.splitlines(),1) if t.strip()]
        parser = "l9-utf8-v1"
    elif fmt == "pdf":
        if not data.startswith(b"%PDF-"): raise RegistryError("PDF signature mismatch")
        # Immutable snapshot avoids using the caller's mutable path during parsing.
        with tempfile.TemporaryDirectory(prefix="l9-") as folder:
            p=Path(folder)/"source.pdf";p.write_bytes(data)
            extraction=ingest(p,metadata)
        elements=[]
        for page in extraction["pages"]:
            for i,b in enumerate(page["blocks"],1):
                elements.append(dict(id=f"p{page['page']}-b{i}",kind=b["kind"],text=b["text"],
                    locator=dict(kind="pdf_region",page=page["page"],bbox=b["bbox"],coordinates=extraction["coordinate_system"])))
            for i,t in enumerate(page["tables"],1):
                elements.append(dict(id=f"p{page['page']}-table{i}",kind="table",text="",rows=t["rows"],
                    locator=dict(kind="pdf_region",page=page["page"],bbox=t["bbox"],coordinates=extraction["coordinate_system"])))
        parser=extraction["parser_version"]
    else: raise RegistryError("Unsupported format; no automatic conversion")
    if not elements: raise RegistryError("No content; review required")
    return dict(schema="l9-ir-v1",source_sha256=digest(data),format=fmt,parser=parser,elements=elements)


class Registry:
    def __init__(self,path):
        self.db=sqlite3.connect(path)
        self.db.row_factory=sqlite3.Row
        self.db.executescript('''
          CREATE TABLE IF NOT EXISTS docs(id TEXT PRIMARY KEY,version INTEGER,access TEXT,state TEXT,
            title TEXT,format TEXT,sha TEXT,source BLOB,ir TEXT);
          CREATE TABLE IF NOT EXISTS chunks(doc TEXT,version INTEGER,element TEXT,text TEXT,
            PRIMARY KEY(doc,version,element));
          CREATE TABLE IF NOT EXISTS requests(key TEXT PRIMARY KEY,fingerprint TEXT,doc TEXT,version INTEGER);
          CREATE TABLE IF NOT EXISTS meta(generation INTEGER);
          INSERT INTO meta SELECT 0 WHERE NOT EXISTS(SELECT 1 FROM meta);
        ''')
        self.db.commit()

    def close(self): self.db.close()

    @property
    def generation(self): return self.db.execute("SELECT generation FROM meta").fetchone()[0]

    def bump(self): self.db.execute("UPDATE meta SET generation=generation+1")

    def upload(self,path,metadata,key):
        authorize(metadata)  # before file read; registered metadata is trusted.
        if not isinstance(key,str) or not 1<=len(key)<=100: raise RegistryError("Invalid request key")
        fmt=Path(path).suffix.lower().lstrip(".")
        if fmt not in ("pdf","txt"): raise RegistryError("Unsupported format")
        if Path(path).stat().st_size>8_000_000: raise RegistryError("Byte limit")
        data=Path(path).read_bytes()
        if not data or len(data)>8_000_000: raise RegistryError("Byte limit/empty source")
        identity=json.dumps(dict(id=metadata['id'],version=metadata['version'],title=metadata['title'],access=metadata['access'],format=fmt,sha=digest(data)),sort_keys=True)
        fingerprint=digest(identity.encode())
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            prior=self.db.execute("SELECT * FROM requests WHERE key=?",(key,)).fetchone()
            if prior:
                current=self.db.execute("SELECT * FROM docs WHERE id=?",(prior['doc'],)).fetchone()
                if prior['fingerprint']!=fingerprint: raise RegistryError("Idempotency key conflict")
                if not current or current['version']!=prior['version'] or current['state']=='deleted' or current['access']!='staff': raise RegistryError("Replay no longer eligible")
                return dict(id=current['id'],version=current['version'],state=current['state'],replayed=True)
            old=self.db.execute("SELECT * FROM docs WHERE id=?",(metadata['id'],)).fetchone()
            if old and old['state']=='deleted': raise RegistryError("Tombstoned ID; use new ID")
            if old and old['access']!='staff': raise RegistryError("Restricted existing source")
            version=1 if old is None else old['version']+1
            self.db.execute("DELETE FROM chunks WHERE doc=?",(metadata['id'],))
            self.db.execute("INSERT OR REPLACE INTO docs VALUES(?,?,?,?,?,?,?,?,?)",(metadata['id'],version,'staff','uploaded',metadata['title'],fmt,digest(data),data,None))
            self.db.execute("INSERT INTO requests VALUES(?,?,?,?)",(key,fingerprint,metadata['id'],version));self.bump()
        return dict(id=metadata['id'],version=version,state='uploaded',replayed=False)

    def eligible(self,id,version):
        row=self.db.execute("SELECT * FROM docs WHERE id=?",(id,)).fetchone()
        if not row or row['version']!=version or row['access']!='staff' or row['state']=='deleted': raise RegistryError("Stale/restricted/deleted source")
        return row

    def parse(self,id,version):
        row=self.eligible(id,version)
        if row['state']!='uploaded': raise RegistryError("Expected uploaded")
        metadata=dict(id=id,version=str(version),access='staff',current=True,title=row['title'])
        ir=parse_bytes(row['source'],row['format'],metadata)
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            current=self.eligible(id,version)
            if current['state']!='uploaded' or current['sha']!=ir['source_sha256']: raise RegistryError("Source changed while parsing")
            self.db.execute("UPDATE docs SET ir=?,state='parsed' WHERE id=?",(json.dumps(ir,ensure_ascii=False),id));self.bump()
        return ir

    def index(self,id,version):
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            row=self.eligible(id,version)
            if row['state'] not in ('parsed','indexed','review'): raise RegistryError("Expected parsed/indexed/review")
            ir=json.loads(row['ir'])
            self.db.execute("DELETE FROM chunks WHERE doc=?",(id,))
            self.db.executemany("INSERT INTO chunks VALUES(?,?,?,?)",[(id,version,e['id'],e['text']) for e in ir['elements'] if e['text'].strip()])
            self.db.execute("UPDATE docs SET state='indexed' WHERE id=?",(id,));self.bump()

    def review(self,id,version):
        with self.db:
            row=self.eligible(id,version)
            if row['state']!='indexed': raise RegistryError("Expected indexed")
            self.db.execute("UPDATE docs SET state='review' WHERE id=?",(id,));self.bump()

    def restrict(self,id,version):
        with self.db:
            self.eligible(id,version)
            self.db.execute("UPDATE docs SET access='restricted' WHERE id=?",(id,))
            self.db.execute("DELETE FROM chunks WHERE doc=?",(id,));self.bump()

    def delete(self,id,version):
        with self.db:
            row=self.db.execute("SELECT * FROM docs WHERE id=?",(id,)).fetchone()
            if not row or row['version']!=version: raise RegistryError("Unknown version")
            self.db.execute("DELETE FROM chunks WHERE doc=?",(id,))
            self.db.execute("UPDATE docs SET state='deleted',source=NULL,ir=NULL,title='',sha='' WHERE id=?",(id,));self.bump()

    def search(self,query):
        if not isinstance(query,str) or not query.strip() or len(query)>200: raise RegistryError("Invalid query")
        # Literal substring search, not SQL LIKE, semantic search or calibrated ranking.
        rows=self.db.execute("SELECT c.* FROM chunks c JOIN docs d ON c.doc=d.id AND c.version=d.version WHERE d.access='staff' AND d.state IN ('indexed','review') ORDER BY c.doc,c.element")
        return dict(generation=self.generation,hits=[dict(r) for r in rows if query in r['text']])

    def context(self,selection):
        if selection['generation']!=self.generation: raise RegistryError("Stale selection")
        result=[]
        for hit in selection['hits']:
            row=self.eligible(hit['doc'],hit['version'])
            if row['state'] not in ('indexed','review'): raise RegistryError("Not indexed")
            ir=json.loads(row['ir']);element=next((e for e in ir['elements'] if e['id']==hit['element'] and e['text'].strip()),None)
            if element is None: raise RegistryError("Unknown element")
            # Canonical text/locator, ignoring caller-supplied text and coordinates.
            result.append(dict(doc=row['id'],version=row['version'],source_sha256=row['sha'],parser=ir['parser'],element=element,review_required=True))
        return result
