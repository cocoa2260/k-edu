"""K-Edu pilot artifact checks; semantic judgments remain a separate Work review."""
import argparse
import hashlib
import json
import re
from pathlib import Path

def blob(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def check(run,attempt,overrides=None):
    overrides=overrides or {}
    def read(name):return overrides.get(name,json.loads((attempt/name).read_text()))
    manifest=json.loads((run/'sources.json').read_text())
    task=json.loads((run/'task.json').read_text())
    sources={f['id']:f for f in manifest['files']}
    def source_path(f):
        local=run/f['local_file']
        return local if local.is_file() else Path(__file__).resolve().parents[3]/f['path']
    texts={k:source_path(v).read_text() for k,v in sources.items()}
    rows={k:v.splitlines() for k,v in texts.items()}
    remote={f['id']:f['sha'] for f in json.loads((run/'remote-verification.json').read_text())['files']}
    findings=read('findings.json')['findings']; coverage=read('coverage.json'); claims=read('execution_claims.json')
    report=(attempt/'analysis.md').read_text()
    results=[]
    def result(id,errors,scope):results.append({'id':id,'status':'fail' if errors else 'pass','errors':errors,'scope':scope})
    errors=[]
    expected={v['source_id']:v for v in [task['target'],*task['comparisons']]}
    if manifest['commit']!=task['source_commit']:errors.append('commit mismatch')
    if set(expected)!=set(sources):errors.append('source set mismatch')
    for sid,f in sources.items():
        if expected[sid]['path']!=f['path'] or expected[sid]['blob_sha']!=f['blob_sha'] or remote.get(sid)!=f['blob_sha']:errors.append(sid+' source identity mismatch')
        if blob(source_path(f).read_bytes())!=f['blob_sha']:errors.append(sid+' blob mismatch')
    result('A01',errors,f'Locked commit, {len(sources)} paths, locally recomputed Git blobs and GitHub blob metadata.')
    required={'id','concept','source_refs','comparison_refs','relation','new_learning_outcome','recommendation','reason','decision_required','verification_status'}
    errors=[];ids=[]
    allowed_recs={'유지','짧게 연결','차별화','통합 후보','삭제 후보','판단 보류'}
    allowed_relations={'similar_explanation','partial_overlap','scope_limited','deeper_treatment','internal_inconsistency','new_within_scope','mixed_recap_and_application','metadata_and_orientation'}
    for f in findings:
        if not required.issubset(f):errors.append('missing finding fields');continue
        ids.append(f['id'])
        if not isinstance(f['decision_required'],bool) or f['recommendation'] not in allowed_recs or f['relation'] not in allowed_relations:errors.append(f['id']+' invalid field type/value')
        if f['verification_status'] not in {'inspected','comparison_insufficient','technical_verification_pending'}:errors.append(f['id']+' invalid verification status')
        if not all(isinstance(f[k],str) and f[k] for k in ['id','concept','relation','new_learning_outcome','reason']):errors.append(f['id']+' empty text')
        if not isinstance(f['source_refs'],list) or not f['source_refs'] or not isinstance(f['comparison_refs'],list):errors.append(f['id']+' invalid references list')
        if f['relation']=='similar_explanation' and not f['comparison_refs']:errors.append(f['id']+' one-sided overlap')
    if len(ids)!=len(set(ids)):errors.append('duplicate finding id')
    for n in ['findings.json','coverage.json','execution_claims.json','analysis.md']:
        if not (attempt/n).is_file():errors.append('missing '+n)
    result('A02',errors,'Required artifact fields, types, allowed values and unique IDs.')
    errors=[];ref_count=0
    for f in findings:
        for ref in f['source_refs']+f['comparison_refs']:
            ref_count+=1;sid=ref.get('source_id');a=ref.get('start_line');b=ref.get('end_line');q=ref.get('quote_line')
            if sid not in rows or not all(isinstance(n,int) for n in [a,b,q]) or not 1<=a<=q<=b<=len(rows[sid]):errors.append(f['id']+' invalid range');continue
            if ref.get('excerpt')!=rows[sid][q-1]:errors.append(f['id']+' excerpt mismatch')
    result('A03',errors,f'{ref_count} source/comparison references: valid lines and exact excerpt text. Does not judge semantic support.')
    errors=[];cursor=1
    for c in coverage['blocks']:
        if c['start_line']!=cursor or c['end_line']<c['start_line']:errors.append(c['id']+' gap/overlap')
        cursor=c['end_line']+1
        if c['status'] not in {'검토함','비교 불충분','해당 없음'} or not c.get('reason'):errors.append(c['id']+' missing status/reason')
        if not c['findings'] or not set(c['findings']).issubset(ids):errors.append(c['id']+' invalid finding links')
        for n in c['findings']:
            f=next(f for f in findings if f['id']==n)
            if not any(r['source_id']=='S04' and r['start_line']<=c['end_line'] and r['end_line']>=c['start_line'] for r in f['source_refs']):errors.append(c['id']+' finding has no overlapping target reference')
    if cursor!=len(rows['S04'])+1 or coverage['total_lines']!=len(rows['S04']):errors.append('target not completely covered')
    result('A04',errors,'38 logical blocks form a non-overlapping partition of all target lines, including metadata/references.')
    errors=[]
    for sid,f in sources.items():
        if blob(source_path(f).read_bytes())!=f['blob_sha']:errors.append(sid+' protected bytes changed')
    allowed={'analysis.md','findings.json','coverage.json','execution_claims.json','review.json','automatic_checks.json'}
    unexpected=[p.name for p in attempt.iterdir() if p.is_file() and p.name not in allowed]
    if unexpected:errors.append('unexpected attempt outputs: '+','.join(unexpected))
    result('A05',errors,f'{len(sources)} protected source files unchanged; attempt output names allowlisted. Remote changed paths checked separately after publication.')
    errors=[];fence=None
    for line in report.splitlines():
        m=re.match(r'^ {0,3}(`{3,}|~{3,})(.*)$',line)
        if not m:continue
        marker,tail=m.groups()
        if fence is None:fence=(marker[0],len(marker))
        elif marker[0]==fence[0] and len(marker)>=fence[1] and not tail.strip():fence=None
    if fence:errors.append('unclosed fence')
    for url in re.findall(r'\]\((https://[^\s]+)\)',report):
        if '/blob/' in url:
            if not any(url.startswith(f['url']+'#L') or url==f['url'] for f in sources.values()):errors.append('unlocked source URL')
            m=re.search(r'#L(\d+)-L(\d+)$',url)
            if m:
                f=next((f for f in sources.values() if url.startswith(f['url']+'#')),None)
                if not f or not 1<=int(m[1])<=int(m[2])<=f['line_count']:errors.append('invalid URL line anchor')
    for f in findings:
        if f['id'] not in report:errors.append('finding missing from report '+f['id'])
    if '\ufffd' in report:errors.append('replacement character')
    result('A06',errors,'Markdown fences, UTF-8 replacement characters and immutable source link/anchor structure; no live external URL checks.')
    errors=[]
    for name in ['lesson_code_executed','ollama_verified','rag_verified','multi_agent_verified']:
        if claims.get(name) is not False:errors.append('unsupported execution claim '+name)
    if claims.get('external_model_api_calls')!=0:errors.append('external model API limit')
    for k in ['input_tokens','output_tokens','tool_calls']:
        if claims.get(k) is not None:errors.append('unexposed usage must be null '+k)
    if claims.get('telemetry_complete') is not False:errors.append('telemetry must be partial')
    result('A07',errors,'Structured execution claims and exposed usage only; prose additionally reviewed under Q05.')
    errors=[]
    attempts=sorted(p.name for p in run.glob('attempt-*') if p.is_dir())
    if len(attempts)>task['limits']['max_attempts']:errors.append('attempt limit')
    events=[json.loads(l) for l in (run/'events.jsonl').read_text().splitlines() if l]
    num=int(attempt.name.split('-')[-1]);required_event='draft_created' if num==1 else 'repair_completed'
    if not any(e['event']==required_event and e.get('attempt')==num for e in events):errors.append('missing attempt event')
    if num>1 and not (run/'attempt-01/review.json').is_file():errors.append('repair lacks prior review')
    result('A08',errors,'Attempt cap and recorded draft/repair checkpoints; soft deadline evaluated by caller between stages.')
    return {'passed':all(c['status']=='pass' for c in results),'checks':results}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('run_dir',type=Path);ap.add_argument('attempt');args=ap.parse_args()
    out=check(args.run_dir,args.run_dir/args.attempt)
    (args.run_dir/args.attempt/'automatic_checks.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(out,ensure_ascii=False,indent=2));raise SystemExit(0 if out['passed'] else 1)
