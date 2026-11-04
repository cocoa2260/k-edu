"""Small arithmetic and historical retrieval-record reader; never loads a model."""
import argparse
from collections import Counter
import json
import math
from pathlib import Path

from retrieval.encoder import profile_hash
from retrieval.index import terms

ROOT = Path(__file__).resolve().parents[2]


def vector_math():
    q = [1.0, 0.0]
    candidates = {"A": [0.8, 0.6], "B": [2.0, 2.0]}
    rows = []
    for name, v in candidates.items():
        norm = math.sqrt(sum(x*x for x in v))
        unit = [x/norm for x in v]
        rows.append(dict(candidate=name, norm=norm,
            dot=sum(a*b for a,b in zip(q,v)),
            cosine=sum(a*b for a,b in zip(q,unit)),
            l2=math.sqrt(sum((a-b)**2 for a,b in zip(q,v))),
            normalized=unit,
            unit_l2_squared=sum((a-b)**2 for a,b in zip(q,unit))))
    # Toy hidden states, not measured E5 output. Padding must not affect the mean.
    hidden, mask = [[1.0, 0.0], [0.0, 2.0], [9.0, 9.0]], [1, 1, 0]
    pooled = [sum(v[i]*m for v,m in zip(hidden,mask))/sum(mask) for i in range(2)]
    length = math.sqrt(sum(x*x for x in pooled))
    rankings = [["A", "B", "C"], ["B", "C", "A"]]
    scores = {name:sum(1/(60+ranking.index(name)+1) for ranking in rankings)
              for name in ["A", "B", "C"]}
    return dict(evidence_kind="toy_arithmetic_not_model_output", vectors=rows,
        masked_mean=pooled, masked_mean_unit=[x/length for x in pooled],
        rrf_scores=scores, rrf_order=sorted(scores,key=lambda x:-scores[x]))


def lexical_example():
    cases = json.loads((ROOT/'data/core-v1.json').read_text())['cases']
    docs = json.loads((ROOT/'data/documents-v1.json').read_text())['documents']
    question = next(c['question'] for c in cases if c['id']=='C08')
    q_terms = set(terms(question))
    rows = []
    for doc in docs:
        if doc['access']!='staff' or not doc['current']:
            continue
        for line, text in enumerate(doc['text'].splitlines(), 1):
            if not text.strip():
                continue
            counts = Counter(terms(doc['title']+'\n'+text))
            rows.append(dict(chunk_id=f"{doc['id']}@{doc['version']}:L{line}",
                matching_terms=sorted(q_terms & counts.keys())))
    return dict(evidence_kind="current_lexical_inspection_not_dense_inference",
                question=question, query_terms=terms(question), chunks=rows)


def read_record(path):
    data = json.loads(path.read_text())
    if (data.get('evidence_kind')!='actual_pinned_embedding_and_sqlite_search_cpu'
            or data.get('answer_generation_calls')!=0 or data.get('paid_api_calls')!=0):
        raise ValueError('Expected an actual retrieval-only record, not generated answers or toy output')
    manifest = data['manifest_before_mutation']
    consistent = profile_hash(manifest['profile'])==manifest['profile_sha256']
    # Report the historical inconsistency, rather than silently rewriting its profile.
    return data, consistent


def show_record(path, case_id):
    data, consistent = read_record(path)
    print(f"저장된 검색 기록 읽기: {path}")
    print('지금 모델을 실행한 결과가 아닙니다. 답변 생성·사실성 평가는 포함하지 않습니다.')
    profile = data['manifest_before_mutation']['profile']
    print(f"모델={profile['model_id']}; 차원={profile['dimension']}; 저장된 Token 상한={profile['max_tokens']}")
    print('설정 표시값/해시 일치:', consistent)
    if not consistent:
        print('주의: 설정 표시값과 당시 해시가 다릅니다. 원본을 유지하고 이번 교안의 기록 주의를 확인하세요.')
    if case_id is None:
        for method, metric in data['metrics'].items():
            print(f"{method}: 평가 {metric['scored_cases']}개, 문서 회수 평균 {metric['mean_document_recall_at_3_chunks']:.4%}, 첫 결과 관련 문서 {metric['relevant_hit_at_1']:.2%}")
        return
    selected = [row for row in data['cases'] if row['case_id']==case_id]
    if not selected:
        raise ValueError(f'No recorded case: {case_id}')
    for row in selected:
        print(f"\n{row['method']} / 상태={row['status']} / 필요한 문서 회수={row.get('document_recall_at_3_chunks')}")
        for rank, hit in enumerate(row['hits'], 1):
            print(f"  {rank}. {hit['chunk_id']} | 점수 {hit['score']} | {hit['text']}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--math', action='store_true')
    mode.add_argument('--lexical', action='store_true')
    mode.add_argument('--record', type=Path)
    parser.add_argument('--case', help='Recorded case ID; requires --record')
    args = parser.parse_args()
    if args.case is not None and args.record is None:
        parser.error('--case requires --record')
    try:
        if args.math:
            print(json.dumps(vector_math(), ensure_ascii=False, indent=2))
        elif args.lexical:
            print(json.dumps(lexical_example(), ensure_ascii=False, indent=2))
        else:
            show_record(args.record, args.case)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(2, f'기록/입력 확인 필요: {exc}\n')


if __name__=='__main__':
    main()
