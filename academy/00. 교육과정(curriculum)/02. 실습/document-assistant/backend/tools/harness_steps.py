"""Read a bounded harness execution in human terms. All live demos are fixtures.

python -m tools.harness_steps
python -m tools.harness_steps --input runs/harness.json --scenario repair_then_success
python -m tools.harness_steps --input runs/harness.json --compare
python -m tools.harness_steps --boundaries
"""
import argparse
import json
from pathlib import Path

from app.harness import run_harness
from tools.harness_demo import ScriptedProvider, draft

WORKED_ANSWER = "사전 승인을 받은 국내 당일 출장 식비 상한은 30,000원입니다. 영수증이 필요하며 식사가 제공되면 지급하지 않습니다."
EVENTS = {"prepared": "최종 입력 준비", "call_started": "Provider 호출 시도",
          "transport_failed": "통신 실패", "retry_scheduled": "같은 입력 재시도 예약",
          "output_checked": "출력 검사", "repair_scheduled": "검사 실패 안내로 보완 예약",
          "provider_failed": "Provider 오류", "input_rejected": "입력 거부", "stopped": "종료"}
FAILURES = {"OUTPUT_CONTRACT": "출력 형식/필드 계약 실패", "CITATION_NOT_SUPPLIED": "제공하지 않은 문서 인용",
            "OUTPUT_SIZE_OR_TYPE": "응답 크기/자료형 실패", "ProviderTimeoutError": "응답 시간 초과",
            "ProviderConnectionError": "연결 실패", "ProviderUpstreamError": "원격 오류 상태"}
STOPS = {"structure_passed_review_required": "구조 통과·사람 검토 필요", "repair_limit": "보완 예산 소진",
         "retry_limit": "재시도 예산 소진", "call_limit": "총 호출 상한", "provider_error": "Provider 오류 종료",
         "cancelled": "취소 신호로 종료", "elapsed_limit": "호출 전후 경과시간 초과",
         "input_rejected": "호출 전 입력 거부", "repair_input_limit": "보완 입력 문자 제한"}


def worked_example():
    provider = ScriptedProvider([draft(WORKED_ANSWER)])
    return run_harness(provider, "C01")


def show_trace(result):
    if result["provider"] != "scripted-fixture" or result["model"] != "no-model-executed":
        raise ValueError("이 읽기 도구는 고정 응답 실험 기록만 다룹니다")
    print("고정 응답 실행 기록입니다. 실제 모델 추론·정답률이 아닙니다.")
    first_input = None
    previous_input = None
    for event in result["trace"]:
        info = []
        if event["event"] == "call_started":
            fingerprint = event["prompt_sha256"]
            if first_input is None:
                first_input = fingerprint
            info.append("첫 입력과 같음" if fingerprint == first_input else "첫 입력에서 변경됨")
            if previous_input is not None:
                info.append("직전 호출과 같음" if fingerprint == previous_input else "직전 호출에서 변경됨")
            previous_input = fingerprint
        if event.get("failure_id"):
            code = event["failure_id"]
            info.append(FAILURES.get(code, code) + " (" + code + ")")
        if event["event"] == "output_checked" and event.get("failure_id") is None:
            info.append("구조/제공 ID 검사 통과")
        if event.get("reason"):
            info.append(STOPS.get(event["reason"], event["reason"]))
        print(f'{event["seq"]}. {EVENTS.get(event["event"], event["event"])} | '
              f'호출 누적 {event["calls"]} | ' + " / ".join(info))
    print(f'\nProvider 시도 {result["calls"]}, 통신 재시도 {result["retries"]}, 보완 {result["repairs"]}')
    print("종료:", STOPS.get(result["stop_reason"], result["stop_reason"]))
    if result["draft"]:
        print("검토할 초안:", result["draft"]["answer"])
        print("출처 ID:", result["draft"]["citations"])
    else:
        print("초안 없음")
    print("내용 검증:", result["factuality_verified"], "/ 승인:", result["approval_granted"])
    print("실제 외부 작업:", result["side_effects_executed"], "/ Token·비용:", result["usage"])


def load_record(path):
    record = json.loads(path.read_text())
    if (record.get("evidence_kind") != "observed_execution_of_scripted_fixtures"
            or record.get("actual_model_calls") != 0 or record.get("paid_api_calls") != 0):
        raise ValueError("고정 응답 데모 기록이 아닙니다. 실제 모델 기록으로 바꾸어 표시하지 않습니다")
    return record


def show_comparison(record):
    names = {"C01": "식비 문의", "C02": "교육비 지원", "C07": "첨부 메모 지시"}
    print("같은 12개 사례에 주입한 고정 출력 A/B 비교입니다. 모델/Prompt 성능표가 아닙니다.")
    for name, rows in record["regression"]["versions"].items():
        passed = sum(row["structural_validation_passed"] for row in rows)
        rejected = sum(row["stop_reason"] == "input_rejected" for row in rows)
        print(f'{name}: 전체 {len(rows)}사례 중 구조 통과 {passed}건, 호출 전 입력 거부 {rejected}건')
    for row in record["regression"]["changes"]:
        label = names.get(row["case_id"], row["case_id"])
        print(f'{label} ({row["case_id"]}): 구조 통과 {row["before"]} → {row["after"]}')
    print("자동 채택하지 않습니다. 전체 구조 수뿐 아니라 회귀와 사람의 내용/행동 검토가 필요합니다.")


def boundary_runs():
    now = [0.0]

    class Late(ScriptedProvider):
        def generate(self, message):
            now[0] = 91.0
            return super().generate(message)

    late = run_harness(Late([draft(WORKED_ANSWER)]), "C01", clock=lambda: now[0])
    flag = {"cancelled": False}

    class Cancelling(ScriptedProvider):
        def generate(self, message):
            flag["cancelled"] = True
            return super().generate(message)

    cancelled = run_harness(Cancelling([draft(WORKED_ANSWER)]), "C01",
                            cancelled=lambda: flag["cancelled"])
    return {"late": late, "cancelled": cancelled}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="harness_demo로 만든 JSON 기록")
    parser.add_argument("--scenario", help="기록에서 읽을 실제 실험 이름. 기본 valid_shape")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--compare", action="store_true")
    modes.add_argument("--boundaries", action="store_true")
    args = parser.parse_args(argv)
    if args.boundaries and (args.input or args.scenario):
        parser.error("시계/취소 시연에는 --input/--scenario를 함께 쓰지 않습니다")
    if args.compare and args.scenario:
        parser.error("전체 비교와 개별 실험 읽기를 분리하세요")
    if (args.compare or args.scenario) and not args.input:
        parser.error("기존 실험을 읽으려면 --input 기록 파일을 지정하세요")
    try:
        if args.boundaries:
            print("가짜 시계·취소 신호의 현재 실행입니다. 실제로 91초 기다리거나 요청을 강제 중단하지 않습니다.")
            for name, result in boundary_runs().items():
                print("\n" + ("호출 중 시계 91초로 변경" if name == "late" else "호출 중 취소 신호 설정"))
                show_trace(result)
        elif args.input:
            record = load_record(args.input)
            if args.compare:
                show_comparison(record)
            else:
                scenario = args.scenario or "valid_shape"
                if scenario not in record["scenarios"]:
                    raise ValueError("기록에 없는 실험 이름입니다")
                show_trace(record["scenarios"][scenario])
        else:
            print("교육용으로 작성한 식비 답안을 고정 반환하고 실제 실행기를 한 번 실행합니다.")
            show_trace(worked_example())
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(2, f"기록/관찰 확인 실패: {exc}\n")


if __name__ == "__main__":
    main()
