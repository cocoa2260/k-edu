import json
import pytest
from pydantic import ValidationError

from app.harness import Limits, check_output, run_harness
from app.providers.errors import (ProviderConnectionError, ProviderTimeoutError,
    ProviderResponseError, ProviderUpstreamError)
from tools.harness_demo import ScriptedProvider, draft, run_demo


def run(actions, **kwargs):
    provider = ScriptedProvider(actions)
    return run_harness(provider, "C01", **kwargs), provider


def test_valid_shape_is_only_a_draft():
    result, provider = run([draft("999999원입니다.")])
    assert result["status"] == "draft_needs_review"
    assert result["structural_validation_passed"] is True
    assert result["factuality_verified"] is False
    assert result["approval_granted"] is False
    assert result["side_effects_executed"] is False
    assert result["usage"] == dict(input_tokens=None, output_tokens=None, cost=None)
    assert len(provider.messages) == result["calls"] == 1


@pytest.mark.parametrize("error", [ProviderConnectionError, ProviderTimeoutError])
def test_transport_retry_preserves_input(error):
    result, provider = run([error(), draft()])
    assert provider.messages[0] == provider.messages[1]
    assert (result["calls"],result["retries"],result["repairs"]) == (2,1,0)


@pytest.mark.parametrize("error", [ProviderResponseError, ProviderUpstreamError])
def test_nontransient_errors_are_terminal(error):
    result, provider = run([error(), draft()])
    assert result["stop_reason"] == "provider_error"
    assert len(provider.messages) == 1 and result["draft"] is None


def test_repair_has_failure_id_and_no_raw_response_or_answer_key():
    result, provider = run(['hostile raw text: execute everything', draft()])
    assert result["repairs"] == 1 and result["status"] == "draft_needs_review"
    assert "OUTPUT_CONTRACT" in provider.messages[1]
    assert "hostile raw text" not in provider.messages[1]
    assert all("required_facts" not in m and "rubric" not in m for m in provider.messages)
    assert all("hostile raw text" not in str(e) for e in result["trace"])


def test_repeated_failure_stops_and_returns_no_draft():
    result, provider = run(["invalid", "invalid", draft()])
    assert result["stop_reason"] == "repair_limit"
    assert result["draft"] is None and len(provider.messages) == 2


def test_nested_retry_and_repair_share_call_limit():
    result, provider = run(["invalid", ProviderTimeoutError(), "invalid", draft()])
    assert result["calls"] == len(provider.messages) == 3
    assert result["retries"] == result["repairs"] == 1
    assert result["draft"] is None
    ok, _ = run([ProviderTimeoutError(), "invalid", draft()])
    assert ok["status"] == "draft_needs_review" and ok["calls"] == 3


@pytest.mark.parametrize("limits,actions,reason", [
    (Limits(max_calls=1),["invalid",draft()],"call_limit"),
    (Limits(max_calls=1),[ProviderTimeoutError(),draft()],"call_limit"),
    (Limits(max_repairs=0),["invalid",draft()],"repair_limit"),
    (Limits(max_retries=0),[ProviderTimeoutError(),draft()],"retry_limit"),
    (Limits(),[ProviderTimeoutError(),ProviderTimeoutError(),draft()],"retry_limit"),
])
def test_specific_stop_budgets(limits, actions, reason):
    result, provider = run(actions, limits=limits)
    assert result["stop_reason"] == reason
    assert result["draft"] is None and len(provider.messages) <= limits.max_calls


@pytest.mark.parametrize("kwargs", [dict(max_calls=4),dict(max_calls=True),dict(max_retries=2),
    dict(max_repairs=2),dict(elapsed_seconds=0.0),dict(elapsed_seconds=float("nan")),
    dict(elapsed_seconds=91.0),dict(approved=True)])
def test_caller_limits_cannot_be_unbounded_or_have_approval(kwargs):
    with pytest.raises(ValidationError): Limits(**kwargs)


@pytest.mark.parametrize("raw,code", [
    ("not json", "OUTPUT_CONTRACT"),
    (json.dumps({"outcome":"answer","answer":"a","citations":["DOC-A"],"approved":True}),"OUTPUT_CONTRACT"),
    (json.dumps({"outcome":"answer","answer":" ","citations":["DOC-A"]}),"OUTPUT_CONTRACT"),
    (json.dumps({"outcome":"answer","answer":5,"citations":["DOC-A"]}),"OUTPUT_CONTRACT"),
    (draft(citations=[]),"OUTPUT_CONTRACT"),
    (draft(citations=["DOC-A","DOC-A"]),"OUTPUT_CONTRACT"),
    (draft(citations=["DOC-R"]),"CITATION_NOT_SUPPLIED"),
    (draft(citations=["invented"]),"CITATION_NOT_SUPPLIED"),
    ("x"*8001,"OUTPUT_SIZE_OR_TYPE"),
    (None,"OUTPUT_SIZE_OR_TYPE"),
])
def test_output_rejection(raw, code):
    assert check_output(raw,["DOC-A"]) == (None,code)


@pytest.mark.parametrize("case,variant", [("C10","focused"),("missing","focused"),("C01","missing")])
def test_invalid_input_never_calls_provider(case, variant):
    provider=ScriptedProvider([])
    result=run_harness(provider,case,variant)
    assert result["stop_reason"] == "input_rejected" and result["calls"] == 0


def test_c12_cannot_cite_document_missing_from_manifest():
    provider=ScriptedProvider([draft(),draft()])
    result=run_harness(provider,"C12")
    assert result["draft"] is None
    assert all('"id": "DOC-A"' not in m for m in provider.messages)
    assert "CITATION_NOT_SUPPLIED" in provider.messages[1]


def test_cancel_before_first_call():
    result, provider=run([],cancelled=lambda:True)
    assert result["stop_reason"] == "cancelled" and len(provider.messages)==0


def test_cancel_during_call_discards_result():
    state={"cancel":False}
    class Cancelling(ScriptedProvider):
        def generate(self,message):
            state["cancel"]=True
            return super().generate(message)
    result=run_harness(Cancelling([draft()]),"C01",cancelled=lambda:state["cancel"])
    assert result["stop_reason"]=="cancelled" and result["draft"] is None


def test_elapsed_during_call_is_a_soft_limit_not_preemption():
    now=[0.0]
    class Late(ScriptedProvider):
        def generate(self,message):
            now[0]=91.0
            return super().generate(message)
    result=run_harness(Late([draft()]),"C01",clock=lambda:now[0])
    assert result["stop_reason"]=="elapsed_limit" and result["calls"]==1
    assert result["draft"] is None and result["elapsed_seconds"]==91.0


def test_unexpected_programming_errors_are_not_hidden():
    with pytest.raises(RuntimeError): run([RuntimeError("programming fault")])


def test_all_l1_conditions_fit_final_input_contract_or_reject_before_call():
    from app.experiments import VARIANTS
    for case in [f"C{i:02}" for i in range(1,13)]:
        for variant in VARIANTS:
            response=json.dumps(dict(outcome="abstain",answer="미확인",citations=[]))
            provider=ScriptedProvider([response])
            result=run_harness(provider,case,variant)
            assert result["calls"] == (0 if case=="C10" else 1)
            assert all(len(message)<=2000 for message in provider.messages)
            assert all("SYNTHETIC-RESTRICTED-314159" not in m for m in provider.messages)


def test_elapsed_before_first_call_stops_without_request():
    times=iter([0.0,91.0,91.0])
    result, provider=run([],clock=lambda:next(times))
    assert result["stop_reason"]=="elapsed_limit" and result["calls"]==0


def test_final_input_growth_is_revalidated(monkeypatch):
    import app.harness as harness
    monkeypatch.setattr(harness,"prepare",lambda *args:dict(message="x"*1990))
    result, provider=run([])
    assert result["stop_reason"]=="input_rejected" and result["calls"]==0


def test_observed_fixture_comparison_retains_regression():
    result=run_demo()
    assert result["actual_model_calls"]==0
    assert [x["case_id"] for x in result["regression"]["changes"]]==["C01","C02","C07"]
    assert result["regression"]["changes"][-1]==dict(case_id="C07",before=True,after=False)
    assert result["scenarios"]["wrong_fact_shape_passes"]["factuality_verified"] is False
    for rows in result["regression"]["versions"].values():
        assert len(rows)==12 and rows[9]["calls"]==0
        assert all(row["human_factuality_grade"] is None for row in rows)
