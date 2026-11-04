"""Index teaching observations: toy traversal, real SQLite with fixed vectors, saved records.

No E5 inference, FAISS import, generation, network or persistent database. Optional
JSON output uses exclusive creation; the lifecycle database is temporary.
"""
import argparse
from copy import deepcopy
import heapq
import json
import math
from pathlib import Path
import tempfile

from retrieval.encoder import profile_hash
from retrieval.index import LocalIndex, ProfileMismatch, StaleSelection

ROOT = Path(__file__).resolve().parents[2]
POINTS = dict(A=(4, 0), B=(3, 0), C=(0, 1), D=(2, 2), E=(6, 0))
GRAPH = dict(A=['B', 'E'], B=['A'], E=['A', 'D'], D=['E', 'C'], C=['D'])


def distance(a, b):
    return math.sqrt(sum((x-y)**2 for x,y in zip(a,b)))


def toy_search():
    """Handmade L2 examples, NOT an implementation or trace of FAISS/HNSW."""
    query = (0, 0)
    def ranked(ids):
        return sorted(ids, key=lambda name:(distance(query, POINTS[name]), name))
    def greedy(graph, start):
        path = [start]
        while True:
            here = path[-1]
            best = ranked([here, *graph[here]])[0]
            if distance(query, POINTS[best]) >= distance(query, POINTS[here]):
                return path
            path.append(best)
    # A minimal candidate-frontier illustration, not efSearch or HNSW's stopping rule.
    queue, seen, expanded = [(distance(query, POINTS['A']), 'A')], {'A'}, []
    while queue:
        _, name = heapq.heappop(queue)
        expanded.append(name)
        for other in GRAPH[name]:
            if other not in seen:
                seen.add(other)
                heapq.heappush(queue, (distance(query, POINTS[other]), other))
    centers = dict(U=(3, 0), V=(0, 4))  # Manually chosen, not learned centroids.
    cells = {name:[] for name in centers}
    for name, point in POINTS.items():
        chosen = min(centers, key=lambda c:(distance(point, centers[c]), c))
        cells[chosen].append(name)
    cell_order = sorted(centers, key=lambda c:(distance(query, centers[c]), c))
    exact = ranked(POINTS)
    ivf = []
    for probes in (1, 2):
        candidates = [name for cell in cell_order[:probes] for name in cells[cell]]
        top = ranked(candidates)[:2]
        ivf.append(dict(probed_cells=cell_order[:probes], candidates=candidates, top2=top,
                        recall_vs_exact_top2=len(set(top)&set(exact[:2]))/2))
    return dict(evidence_kind='toy_L2_graph_and_cells_not_HNSW_or_FAISS', query=query,
        points=POINTS, distances={name:distance(query,p) for name,p in POINTS.items()},
        exact_order=exact, graph=GRAPH, greedy_path=greedy(GRAPH,'A'),
        frontier_expansion_order=expanded, upper_greedy_path=greedy(dict(A=['D'], D=['A']),'A'),
        lower_path_from_D=greedy(GRAPH,'D'),centers=centers,cells=cells,ivf=ivf)


class FixedEncoder:
    """Nonsemantic unit vectors, solely to observe existing Index behavior."""
    def __init__(self):
        self.profile = dict(model_id='index-teaching-nonsemantic-fixture', revision='v1',
                            dimension=2, normalized=True, max_tokens=512)

    def encode(self, texts, kind):
        return [[1.0, 0.0] for _ in texts]


def lifecycle():
    original = (ROOT/'data/documents-v1.json').read_bytes()
    docs = json.loads(original)['documents']
    encoder = FixedEncoder()
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder)/'index.sqlite'
        index = LocalIndex.create(path, encoder, docs)
        try:
            before = index.manifest()
            all_hits = index.search('국내 당일 출장 식비 상한', k=10)
            selected = index.search('국내 당일 출장 식비 상한', manifest_ids={'DOC-A'}, k=10)
            context_before = index.context(selected)
            forged = deepcopy(selected)
            forged['hits'][0]['text'] = 'FORGED-RESPONSE-TEXT'
            refetched = index.context(forged)
            updated = deepcopy(docs[0])
            updated.update(version='v2-teaching-override', text='1. 갱신 시험용 가상 국내 당일 출장 식비 상한은 35000원이다. 사전 승인·영수증이 필요하다.')
            index.upsert(updated)
            def stale(selection):
                try:
                    index.context(selection)
                except StaleSelection:
                    return True
                raise AssertionError('Old selection was accepted')
            update_rejected = stale(selected)
            after_update = index.manifest()
            fresh = index.search('국내 당일 출장 식비 상한', manifest_ids={'DOC-A'}, k=10)
            context_after_update = index.context(fresh)
            index.delete('DOC-A')
            delete_rejected = stale(fresh)
            after_delete = index.manifest()
            deleted_hits = index.search('국내 당일 출장 식비 상한', k=10)
            tombstone = dict(index.db.execute("SELECT id,version,access,current,deleted,title,text,content_sha FROM documents WHERE id='DOC-A'").fetchone())
            remaining_vectors = index.db.execute("SELECT COUNT(*) FROM chunks WHERE doc_id='DOC-A'").fetchone()[0]
            encoder.profile['max_tokens'] = 128
            try:
                other = LocalIndex(path, encoder)
            except ProfileMismatch:
                mismatch_rejected = True
            else:
                other.close()
                raise AssertionError('Changed profile accepted')
        finally:
            index.close()
        rebuilt = LocalIndex.create(Path(folder)/'rebuilt.sqlite', encoder, docs)
        try:
            rebuilt_manifest = rebuilt.manifest()
            rebuilt_context = rebuilt.context(rebuilt.search('국내 당일 출장 식비 상한',manifest_ids={'DOC-A'},k=10))
        finally:
            rebuilt.close()
    return dict(evidence_kind='current_sqlite_lifecycle_with_nonsemantic_fixed_vectors',
        model_inference_calls=0,original_source_unchanged=(ROOT/'data/documents-v1.json').read_bytes()==original,
        manifest_before=before,eligible_before=all_hits['eligible_chunks'],
        permitted_document_ids=sorted({h['doc_id'] for h in all_hits['hits']}),
        selected_before=selected,context_before=context_before,context_after_text_forgery=refetched,
        stale_after_update_rejected=update_rejected,manifest_after_update=after_update,
        selected_after_update=fresh,context_after_update=context_after_update,
        stale_after_delete_rejected=delete_rejected,manifest_after_delete=after_delete,
        after_delete_document_ids=sorted({h['doc_id'] for h in deleted_hits['hits']}),
        tombstone=tombstone,remaining_DOC_A_vectors=remaining_vectors,
        profile_mismatch_rejected=mismatch_rejected,rebuild_manifest=rebuilt_manifest,
        rebuilt_context=rebuilt_context,
        note='Temporary SQLite removed after observation. Fixed vectors do not test relevance or E5; rebuild restores original v1 data.')


def saved_ann(path):
    data = json.loads(path.read_text())
    if data.get('evidence_kind')!='actual_faiss_search_on_synthetic_unit_vectors':
        raise ValueError('Expected a saved actual FAISS synthetic-vector record')
    k = data['k']
    rows = []
    for row in data['rows']:
        reference = set(row['first_query_exact_ids'])
        found = set(row['first_query_ids'])
        if len(reference)!=k or len(found)!=k or k<=0:
            raise ValueError('Incomplete or duplicated first-query neighbors')
        rows.append(dict(index=row['index'],efSearch=row['efSearch'],nprobe=row['nprobe'],
            saved_mean_recall=row['recall_at_10_vs_exact'],saved_median_batch_ms=row['median_batch_ms'],
            first_query_recall=len(reference&found)/k,first_query_missing_ids=sorted(reference-found)))
    return dict(evidence_kind='reading_saved_FAISS_results_not_rerunning_FAISS',source=str(path),
        vectors=data['vectors'],dimension=data['dimension'],queries=data['queries'],k=k,
        timing=data['timing'],semantic_quality=data['semantic_quality'],rows=rows,
        note='이 파일의 ID로 재계산한 것은 첫 질의의 교집합입니다. 전체 평균은 기존 128질의의 저장값입니다.')


def saved_lifecycle(path):
    data = json.loads(path.read_text())
    if data.get('evidence_kind')!='actual_pinned_embedding_and_sqlite_search_cpu':
        raise ValueError('Expected a saved actual E5/SQLite retrieval record')
    before = data['manifest_before_mutation']
    consistent = profile_hash(before['profile'])==before['profile_sha256']
    return dict(evidence_kind='reading_saved_E5_lifecycle_not_rerunning_model',source=str(path),
        saved_profile_hash_matches_display=consistent,
        initial_total_chunks=before['total_chunks'],
        lifecycle=data['lifecycle'],migration=data['migration'],
        note=('설정 표시값/해시가 일치합니다. 파일 읽기는 새 모델 실행이 아닙니다.' if consistent else
              '설정 표시값/해시 불일치를 확인하세요. 기존 E5 기록의 512/128 오류는 교안에 설명돼 있으며 원본을 바꾸지 않습니다.'))


def display(result):
    kind = result['evidence_kind']
    print('근거 종류:', kind)
    if kind.startswith('toy_'):
        print('가상 좌표의 L2 계산입니다. HNSW/FAISS 실행이나 E5 벡터가 아닙니다.')
        for name in result['exact_order']:
            print(f"{name}: 좌표={result['points'][name]}, 질의와 거리={result['distances'][name]:.4f}")
        for label, key in [('좁은 이웃 이동', 'greedy_path'), ('후보를 남긴 확장 순서', 'frontier_expansion_order'),
                           ('가상 윗층 이동', 'upper_greedy_path'), ('D에서 아랫층 이동', 'lower_path_from_D')]:
            print(label+': '+' → '.join(result[key]))
        print('직접 정한 구역:',result['cells'])
        for row in result['ivf']:
            print(f"탐색 구역={row['probed_cells']}; 상위2={row['top2']}; Exact 이웃 회수={row['recall_vs_exact_top2']}")
    elif kind.startswith('current_sqlite'):
        print('실제 임시 SQLite 동작, 의미 없는 고정 2차원 벡터입니다. 모델 추론은 없습니다.')
        for label, key in [('처음', 'manifest_before'), ('갱신 뒤', 'manifest_after_update'), ('삭제 뒤', 'manifest_after_delete'), ('재구축', 'rebuild_manifest')]:
            m=result[key]
            print(f"{label}: 변경 번호={m['generation']}, 전체 조각={m['total_chunks']}, Token 상한 설정={m['profile']['max_tokens']}")
        hit=result['selected_before']['hits'][0]
        print('선택한 조각:',hit['chunk_id'])
        print('실제 첫 줄:',hit['text'])
        print('원문 위치:',hit['source_locator'])
        print('문서 전체 본문 해시:',hit['content_sha'])
        print('기본 적격 조각:',result['eligible_before'],'/ 검색에 허용된 문서:',result['permitted_document_ids'])
        print('결과 본문을 위조해도 원문 재조회:',result['context_after_text_forgery']==result['context_before'])
        print('갱신 전 선택 거부:',result['stale_after_update_rejected'])
        print('갱신 뒤 새 본문:',result['context_after_update'][0]['text'])
        print('삭제 전 선택 거부:',result['stale_after_delete_rejected'])
        print('삭제 표식:',result['tombstone'],'/ 남은 출장 규정 벡터:',result['remaining_DOC_A_vectors'])
        print('설정 불일치 거부:',result['profile_mismatch_rejected'])
        print('원본 파일 보존:',result['original_source_unchanged'],'/ 임시 DB는 관찰 후 제거됩니다.')
    elif kind.startswith('reading_saved_FAISS'):
        print('저장된 합성 벡터 FAISS 결과를 읽습니다. 지금 FAISS를 실행한 것이 아닙니다.')
        print(f"벡터={result['vectors']}, 차원={result['dimension']}, 질의={result['queries']}, k={result['k']}")
        for row in result['rows']:
            print(f"{row['index']} efSearch={row['efSearch']} nprobe={row['nprobe']}: 저장된 전체 평균={row['saved_mean_recall']:.4%}, 첫 질의={row['first_query_recall']:.0%}, 배치 ms={row['saved_median_batch_ms']:.3f}, 첫 질의 누락={row['first_query_missing_ids']}")
        print(result['note'])
    else:
        print('저장된 실제 E5/SQLite 변경 기록 읽기입니다. 지금 모델을 실행한 것이 아닙니다.')
        print('최초 전체 조각:',result['initial_total_chunks'])
        print('과거 설정 표시값/해시 일치:',result['saved_profile_hash_matches_display'])
        life=result['lifecycle']
        print('갱신 전 선택 거부:',life['stale_after_update_rejected'],'/ 삭제 전 선택 거부:',life['stale_after_delete_rejected'])
        for row in life['context_after_update']:
            print('갱신 뒤 Context:',row['doc_id'],row['version'],row['text'])
        print('삭제 뒤 문서:',life['after_delete_document_ids'])
        print('설정 불일치 거부:',result['migration']['profile_mismatch_rejected'])
        print(result['note'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--toy',action='store_true')
    modes.add_argument('--lifecycle',action='store_true')
    modes.add_argument('--ann-record',type=Path)
    modes.add_argument('--stored-record',type=Path)
    parser.add_argument('--output',type=Path,help='Optional new JSON file; refuses overwrite')
    args = parser.parse_args()
    try:
        if args.output and args.output.exists():
            raise FileExistsError('Output already exists; select a new path')
        if args.toy:
            result = toy_search()
        elif args.lifecycle:
            result = lifecycle()
        elif args.ann_record:
            result = saved_ann(args.ann_record)
        else:
            result = saved_lifecycle(args.stored_record)
        text = json.dumps(result,ensure_ascii=False,indent=2)+'\n'
        if args.output:
            with args.output.open('x') as stream:
                stream.write(text)
        display(result)
        if args.output:
            print('전체 관찰 기록:',args.output)
    except (OSError,ValueError,KeyError,TypeError) as exc:
        parser.exit(2,f'입력/기록 확인 필요: {exc}\n')


if __name__=='__main__':
    main()
