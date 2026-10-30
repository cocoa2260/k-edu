"""Optional FAISS exploration on synthetic vectors, not language-model evidence."""
import argparse
import json
from pathlib import Path
import time


def main():
    import faiss
    import numpy as np
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    if args.output.exists(): raise FileExistsError(args.output)
    faiss.omp_set_num_threads(1)
    rng=np.random.default_rng(20261031)
    data=rng.normal(size=(4096,32)).astype('float32')
    queries=rng.normal(size=(128,32)).astype('float32')
    faiss.normalize_L2(data);faiss.normalize_L2(queries)
    exact=faiss.IndexFlatIP(32);exact.add(data)
    _,reference=exact.search(queries,10)
    hnsw=faiss.IndexHNSWFlat(32,8,faiss.METRIC_INNER_PRODUCT)
    hnsw.hnsw.efConstruction=40;hnsw.add(data)
    ivf=faiss.IndexIVFFlat(faiss.IndexFlatIP(32),32,64,faiss.METRIC_INNER_PRODUCT)
    ivf.cp.seed=20261031;ivf.train(data);ivf.add(data)
    rows=[]
    for name,index,settings in [('exact',exact,[None]),('hnsw',hnsw,[8,64]),('ivf',ivf,[1,16,64])]:
        for setting in settings:
            if name=='hnsw': index.hnsw.efSearch=setting
            if name=='ivf': index.nprobe=setting
            index.search(queries,10)  # Warm-up excluded from timing.
            elapsed=[]
            for _ in range(5):
                started=time.perf_counter();_,ids=index.search(queries,10)
                elapsed.append((time.perf_counter()-started)*1000)
            recall=sum(len(set(a)&set(b))/10 for a,b in zip(ids,reference))/len(queries)
            rows.append(dict(index=name,efSearch=setting if name=='hnsw' else None,
                nprobe=setting if name=='ivf' else None,recall_at_10_vs_exact=recall,
                median_batch_ms=sorted(elapsed)[2],batch_queries=128,
                first_query_ids=ids[0].tolist(),first_query_exact_ids=reference[0].tolist()))
    q=np.array([1.,0.]); a=np.array([.8,.6]); b=np.array([2.,2.])
    math_rows=[]
    for name,v in [('A',a),('B',b)]:
        cosine=float(np.dot(q,v)/(np.linalg.norm(q)*np.linalg.norm(v)))
        unit=v/np.linalg.norm(v)
        math_rows.append(dict(candidate=name,dot=float(q@v),cosine=cosine,
            squared_l2=float(((q-v)**2).sum()),normalized_dot=float(q@unit),
            normalized_squared_l2=float(((q-unit)**2).sum())))
    result=dict(evidence_kind='actual_faiss_search_on_synthetic_unit_vectors',
        faiss_version=faiss.__version__,seed=20261031,rows=rows,
        vector_math=dict(query=q.tolist(),A=a.tolist(),B=b.tolist(),results=math_rows),
        vectors=4096,dimension=32,queries=128,k=10,hnsw_M=8,efConstruction=40,ivf_nlist=64,
        threads=1,timing='warm search; median of 5 batches; excludes encoding/training/build',
        semantic_quality=None,notes=['Not the nine eligible text chunks or E5 corpus',
            'FAISS HNSW removal is not implemented here; SQLite deletion is a separate exact index test'])
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x') as stream: json.dump(result,stream,ensure_ascii=False,indent=2);stream.write('\n')
    print(json.dumps(rows))


if __name__=='__main__': main()
