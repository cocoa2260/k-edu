"""Read the existing prepared inputs; never generate or grade an answer.

From backend: python -m tools.prompt_inputs
Full input: python -m tools.prompt_inputs --case C01 --variant instruction
"""
import argparse

from pydantic import ValidationError

from app.experiments import VARIANTS, prepare


PROMPT_VARIANTS = ("baseline", "instruction", "one_shot", "few_shot")
LABELS = {
    "baseline": "짧은 지시 · 예시 없음",
    "instruction": "구체적인 지시 · 예시 없음",
    "one_shot": "구체적인 지시 · 예시 1개",
    "few_shot": "구체적인 지시 · 예시 2개",
    "focused": "구체적인 지시 · 제공 자료 선택",
}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", default="C01", help="실제 사례 파일의 ID. 기본값은 식비 문의")
    parser.add_argument("--variant", choices=VARIANTS, help="한 조건의 전체 입력 표시")
    args = parser.parse_args(argv)
    variants = (args.variant,) if args.variant else PROMPT_VARIANTS
    try:
        rows = [prepare(args.case, variant) for variant in variants]
    except (ValueError, ValidationError):
        parser.exit(2, "입력 준비 실패: 사례 ID, 공백 질문 또는 2000문자 제한을 확인하세요. 모델은 호출하지 않았습니다.\n")

    question = rows[0]["message"].rsplit("사용자 질문:\n", 1)[1]
    print("질문: " + question)
    print("아래는 준비된 입력입니다. 모델 답변·정답률·Token 계산 결과가 아닙니다.")
    print("조건 | 예시 수 | 제공 자료 수 | 문자 수")
    for row in rows:
        print(f'{LABELS[row["variant"]]} | {row["shot_count"]} | '
              f'{len(row["document_ids"])} | {row["character_count"]}')

    if args.variant:
        print("\n【모델에 전달할 입력 시작】")
        print(rows[0]["message"])
        print("【모델에 전달할 입력 끝】")
    else:
        print("\n실제로 사용한 작성 지시:")
        for row in rows[:2]:
            print(f'\n{LABELS[row["variant"]]}:')
            print(row["message"].split("\n\n", 1)[0])
        print("\n전체 입력: 같은 명령에 --variant instruction을 추가하세요.")
        print("예시가 들어간 전체 입력: --variant one_shot 또는 --variant few_shot")


if __name__ == "__main__":
    main()
