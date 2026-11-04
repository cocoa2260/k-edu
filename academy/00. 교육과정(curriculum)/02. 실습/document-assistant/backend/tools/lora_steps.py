"""Read stored LoRA evidence or run an illustrative scalar calculation. No model calls."""
import argparse
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT.parents[1] / 'reports/KEDU-PRODUCTION-011/observed.json'


def toy_step():
    """Scalar LoRA, squared error and plain SGD; not Qwen/AdamW/Token training."""
    w, a, b, x, target, scale, lr = 1.0, 1.0, 0.0, 2.0, 3.0, 2.0, 0.1
    prediction = w * x + scale * b * a * x
    error = prediction - target
    grad_a, grad_b = error * scale * b * x, error * scale * a * x
    next_a, next_b = a - lr * grad_a, b - lr * grad_b
    next_prediction = w * x + scale * next_b * next_a * x
    return dict(base_weight=w, initial_a=a, initial_b=b, input=x, target=target,
                scale=scale, learning_rate=lr, prediction=prediction, loss=0.5*error**2,
                grad_a=grad_a, grad_b=grad_b, next_a=next_a, next_b=next_b,
                next_prediction=next_prediction, next_loss=0.5*(next_prediction-target)**2)


def macro(evaluation):
    cases = evaluation['cases']
    if not cases:
        raise ValueError('No loss cases')
    return sum(row['loss'] for row in cases) / len(cases)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=['math','training','evaluation','case','regression','reload'], default='training')
    parser.add_argument('--example', default='FT-E01-S04', help='Stored Test example for case mode')
    args = parser.parse_args()
    if args.mode == 'math':
        print('설명용 가상 스칼라 계산: 실제 모델/Optimizer 실행이 아닙니다.')
        print(json.dumps(toy_step(), ensure_ascii=False, indent=2))
        return
    try:
        record = json.loads(RECORD.read_text())
        variants = record['variants']
        print('과거 실제 LoRA 기록 읽기: 지금 모델/훈련/재로드를 실행하지 않습니다.')
        if args.mode == 'training':
            config = record['configuration']
            print('Base/Revision:', config['model_id'], config['revision'])
            print('설정:', {key: config[key] for key in ['r','alpha','dropout','targets','dtype','steps','batch_size','seed']})
            for name in ['seed','augmented']:
                t = variants[name]['training']
                print(name, '고유행/Step/정답 Token:', t['unique_rows_seen'], t['optimizer_steps'], t['supervised_token_exposures'])
                print('학습 가능/전체:', t['trainable_parameters'], t['total_parameters'])
                print('Adapter 변화/동결 표본:', t['adapter_absolute_delta'], t['frozen_weight_samples_unchanged'])
                print('첫/마지막 Step:', t['logs'][0], t['logs'][-1])
        elif args.mode == 'evaluation':
            for name, v in variants.items():
                generations = v['test_generations']
                passed = [r for r in generations if r['contract_failure'] is None]
                matched = sum(r['outcome']==r['expected_outcome'] for r in passed)
                print(name, 'Validation/Test Loss:', round(macro(v['validation']),6), round(macro(v['test_loss']),6),
                      '계약/계약+행동:', len(passed), matched, '/분모:', len(generations))
            print('저장된 Validation 선택:', record['selection'])
        elif args.mode == 'case':
            for name, v in variants.items():
                r = next((x for x in v['test_generations'] if x['id']==args.example), None)
                if r is None:
                    raise ValueError('Unknown Test example')
                print(name, '기대/저장 계약/행동:', r['expected_outcome'], r['contract_failure'], r['outcome'])
                print('저장 원응답:', r['raw_output'])
        elif args.mode == 'regression':
            for name, v in variants.items():
                cases = v['regression']
                calls = sum(len(r['generation_observations']) for r in cases.values())
                drafts = sum(r['draft'] is not None for r in cases.values())
                print(name, '사례/모델 생성/최종 초안:', len(cases), calls, drafts)
                print('종료:', dict(Counter(r['stop_reason'] for r in cases.values())))
        elif args.mode == 'reload':
            for name in ['seed','augmented']:
                reload = variants[name]['fresh_process_reload']
                prior = next(r for r in variants[name]['test_generations'] if r['id']==reload['id'])
                print(name, reload['id'], '저장 Token열 일치:', reload['token_ids']==prior['token_ids'],
                      '과거 HTTP 시도:', reload['http_attempts'], '계약:', reload['contract_failure'])
                print('저장된 Adapter SHA256:', reload['adapter_sha256'])
            print('실제 바이너리 해시나 새 프로세스를 지금 확인한 것은 아닙니다.')
    except (OSError,ValueError,KeyError,TypeError) as exc:
        parser.exit(2, f'자료/기록 확인 필요: {exc}\n')


if __name__ == '__main__':
    main()
