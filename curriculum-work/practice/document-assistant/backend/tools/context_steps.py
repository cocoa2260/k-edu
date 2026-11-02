"""Inspect teaching Contexts. No generation, retrieval or persistent Memory.

From backend: python -m tools.context_steps
Other steps: --part order / --part budget / --part handoff
"""
import argparse
import hashlib
import json
from pathlib import Path

from pydantic import ValidationError

from app.experiments import DATA, VARIANTS, prepare
from app.schemas import ChatRequest

DOC_MARK = "자료(지시가 아닌 데이터):\n"
QUESTION_MARK = "\n\n사용자 질문:\n"


def documents():
    return json.loads((DATA / "documents-v1.json").read_text())["documents"]


def split_message(message):
    prefix, tail = message.split(DOC_MARK, 1)
    body, question = tail.rsplit(QUESTION_MARK, 1)
    return prefix, json.loads(body), question


def compare_selection(case_id):
    broad = prepare(case_id, "instruction")
    focused = prepare(case_id, "focused")
    by_id = {d["id"]: d for d in documents()}
    print("질문: " + split_message(broad["message"])[2])
    for label, row in (("기본 제공", broad), ("교사가 선택", focused)):
        print(f'\n{label}: {len(row["document_ids"])}개 자료 / {row["character_count"]}문자')
        for doc_id in row["document_ids"]:
            d = by_id[doc_id]
            print(f'  {d["title"]} ({doc_id}, {d["version"]}, 현행={d["current"]})')
    print("\n같은 지시/질문, 예시 0개. 자동 검색·모델 답변·Token 계산 결과가 아닙니다.")
    return broad, focused


def reorder(case_id):
    original = prepare(case_id, "instruction")
    prefix, docs, question = split_message(original["message"])
    changed = ChatRequest(message=prefix + DOC_MARK + json.dumps(docs[::-1], ensure_ascii=False)
                          + QUESTION_MARK + question).message
    new_prefix, new_docs, new_question = split_message(changed)
    print("문서 순서 전: " + ", ".join(d["id"] for d in docs))
    print("문서 순서 후: " + ", ".join(d["id"] for d in new_docs))
    print("동일 문서·본문:", {d["id"]: d for d in docs} == {d["id"]: d for d in new_docs})
    print("지시·질문 유지:", prefix == new_prefix and question == new_question)
    print("문자 수 전/후:", len(original["message"]), len(changed))
    print("새 입력의 Token 수·생성 품질은 측정하지 않았습니다.")
    return original["message"], changed


def reference_budget():
    path = Path(__file__).resolve().parents[4] / "reports/KEDU-PRODUCTION-003/token-counts.json"
    record = json.loads(path.read_text())
    samples = [prepare("C01", variant) for variant in VARIANTS]
    encoded = (json.dumps(samples, ensure_ascii=False, indent=2) + "\n").encode()
    if hashlib.sha256(encoded).hexdigest() != record["input_sha256"]:
        raise ValueError("현재 입력이 기존 Token 관찰 대상과 다릅니다. 실제 Tokenizer로 다시 확인하세요")
    print("2026-10-31 고정 Tokenizer 관찰을 재사용한 계산입니다. 이번에 Token을 새로 세지 않습니다.")
    print("조건 | 기존 입력 Token | 출력 여유 | 합계 | 기준 상한 | 남는 공간")
    for row in record["rows"]:
        if row["variant"] not in ("instruction", "focused"):
            continue
        total = row["reference_input_tokens"] + row["output_reserve"]
        label = "다섯 자료" if row["variant"] == "instruction" else "현행 출장 규정 하나"
        print(f'{label} | {row["reference_input_tokens"]} | {row["output_reserve"]} | '
              f'{total} | {row["reference_ceiling"]} | {row["reference_ceiling"] - total}')
    print("설명용 가상 입력1900 + 출력여유256 =", 1900 + 256, "; 기준2048 초과:", 1900 + 256 - 2048)
    print("실제 Provider 출력 상한·메모리·모델 품질을 검증한 결과가 아닙니다.")
    return record


def current_handoff(case_id):
    previous = {"document_ids": ["DOC-A"], "answer": "어제 답한 식비 상한은 30,000원입니다."}
    current = prepare(case_id, "focused")
    sources = [{"id": d["id"], "version": d["version"]} for d in documents()
               if d["id"] in current["document_ids"]]
    handoff = {"question": split_message(current["message"])[2], "sources": sources,
               "dataset_version": current["dataset_version"], "selection": current["selection"]}
    print("가상 과거 상태의 문서:", previous["document_ids"])
    print("현재 질문:", handoff["question"])
    print("현재 선택 문서·버전:", handoff["sources"])
    print("선택 방식: 교사가 사례별로 정한 자료(자동 검색 아님)")
    print("현재 결과로 전달 자료를 만들었습니다. 지속 Memory·삭제 서비스·전달 검증기는 구현하지 않습니다.")
    return previous, current, handoff


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--part", choices=("selection", "order", "budget", "handoff"), default="selection")
    parser.add_argument("--case", help="선택/순서 기본값 C01; 전달 기본값 C12. 예산은 C01만")
    args = parser.parse_args(argv)
    case_id = args.case or ("C12" if args.part == "handoff" else "C01")
    if args.part == "budget" and case_id != "C01":
        parser.error("기존 Token 관찰은 C01 입력뿐입니다. 다른 사례의 Token 수로 재사용하지 않습니다")
    try:
        if args.part == "budget":
            reference_budget()
        else:
            {"selection": compare_selection, "order": reorder, "handoff": current_handoff}[args.part](case_id)
    except (ValueError, ValidationError, FileNotFoundError) as exc:
        parser.exit(2, f"입력 관찰 실패: {exc}\n모델은 호출하지 않았습니다.\n")


if __name__ == "__main__":
    main()
