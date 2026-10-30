"""L2 bounded synchronous harness. Validation is structural, never a fact oracle."""
import hashlib
import time
from collections.abc import Callable
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from app.experiments import prepare
from app.providers.base import AIProvider
from app.providers.errors import (
    ProviderConnectionError, ProviderTimeoutError, ProviderResponseError,
    ProviderUpstreamError,
)
from app.schemas import ChatRequest


class Limits(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)
    max_calls: int = Field(default=3, ge=1, le=3)
    max_retries: int = Field(default=1, ge=0, le=1)
    max_repairs: int = Field(default=1, ge=0, le=1)
    elapsed_seconds: float = Field(default=90.0, gt=0, le=90, allow_inf_nan=False)


class Draft(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    outcome: Literal["answer", "abstain", "clarify", "deny"]
    answer: str = Field(min_length=1, max_length=1500)
    citations: list[str] = Field(max_length=6)

    @model_validator(mode="after")
    def meaningful_shape(self):
        if not self.answer.strip():
            raise ValueError("blank answer")
        if self.outcome == "answer" and not self.citations:
            raise ValueError("answer needs a citation")
        if len(self.citations) != len(set(self.citations)):
            raise ValueError("duplicate citations")
        return self


CONTRACT = (
    '\n\n출력 계약: JSON 객체 하나만 출력하라. 키는 outcome, answer, citations뿐이다. '
    'outcome은 answer/abstain/clarify/deny 중 하나, answer는 비어 있지 않은 문자열, '
    'citations는 제공된 문서 ID의 배열이다. answer 상태는 근거 ID가 하나 이상 필요하다. '
    '승인·도구 실행을 요청하거나 승인 필드를 추가하지 마라.'
)


def digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def check_output(raw: str, allowed_ids: list[str]) -> tuple[Draft | None, str | None]:
    if not isinstance(raw, str) or len(raw) > 8000:
        return None, "OUTPUT_SIZE_OR_TYPE"
    try:
        draft = Draft.model_validate_json(raw)
    except ValidationError:
        return None, "OUTPUT_CONTRACT"
    if not set(draft.citations).issubset(allowed_ids):
        return None, "CITATION_NOT_SUPPLIED"
    return draft, None


def run_harness(
    provider: AIProvider, case_id: str, variant: str = "focused", *,
    limits: Limits | None = None,
    cancelled: Callable[[], bool] = lambda: False,
    clock: Callable[[], float] = time.monotonic,
) -> dict:
    """Caller owns cancellation and limits; neither is read from model output.

    Elapsed limit is checked between synchronous calls. It CANNOT interrupt an
    in-flight provider call. Real adapters have their own transport timeout.
    """
    limits = limits or Limits()
    started = clock()
    trace: list[dict] = []
    calls = retries = repairs = 0

    def event(kind: str, **fields):
        trace.append({"seq": len(trace) + 1, "event": kind, "calls": calls, **fields})

    def finish(reason: str, draft: Draft | None = None):
        event("stopped", reason=reason)
        return {
            "status": "draft_needs_review" if draft else "stopped",
            "stop_reason": reason, "case_id": case_id, "variant": variant,
            "calls": calls, "retries": retries, "repairs": repairs,
            "provider": provider.provider_name, "model": provider.model_name,
            "draft": draft.model_dump() if draft else None,
            "structural_validation_passed": draft is not None,
            "factuality_verified": False, "approval_granted": False,
            "side_effects_executed": False,
            "usage": {"input_tokens": None, "output_tokens": None, "cost": None},
            "elapsed_seconds": round(max(0, clock() - started), 6),
            "deadline_mode": "between_calls_not_inflight_cancellation",
            "limits": limits.model_dump(), "trace": trace,
        }

    try:
        prepared = prepare(case_id, variant)
        original = ChatRequest(message=prepared["message"] + CONTRACT).message
    except (ValidationError, ValueError):
        event("input_rejected")
        return finish("input_rejected")
    event("prepared", document_ids=prepared["document_ids"],
          dataset_version=prepared["dataset_version"], prompt_sha256=digest(original))
    message = original
    while True:
        if cancelled():
            return finish("cancelled")
        if clock() - started >= limits.elapsed_seconds:
            return finish("elapsed_limit")
        if calls >= limits.max_calls:
            return finish("call_limit")
        calls += 1
        event("call_started", prompt_sha256=digest(message))
        try:
            raw = provider.generate(message)
        except (ProviderConnectionError, ProviderTimeoutError) as exc:
            event("transport_failed", failure_id=type(exc).__name__)
            if cancelled():
                return finish("cancelled")
            if clock() - started >= limits.elapsed_seconds:
                return finish("elapsed_limit")
            if calls >= limits.max_calls:
                return finish("call_limit")
            if retries >= limits.max_retries:
                return finish("retry_limit")
            retries += 1
            event("retry_scheduled")  # Identical input, global retry budget.
            continue
        except (ProviderResponseError, ProviderUpstreamError) as exc:
            event("provider_failed", failure_id=type(exc).__name__)
            return finish("provider_error")
        # Unexpected programming errors propagate, rather than masquerading as model failures.
        if cancelled():
            return finish("cancelled")
        if clock() - started >= limits.elapsed_seconds:
            return finish("elapsed_limit")  # Discard a late result.
        draft, failure_id = check_output(raw, prepared["document_ids"])
        event("output_checked", failure_id=failure_id,
              output_sha256=digest(raw) if isinstance(raw, str) else None)
        if draft is not None:
            return finish("structure_passed_review_required", draft)
        if repairs >= limits.max_repairs:
            return finish("repair_limit")
        if calls >= limits.max_calls:
            return finish("call_limit")
        repairs += 1
        # Never insert untrusted model output or evaluation answer keys into feedback.
        try:
            message = ChatRequest(message=original +
                f"\n검사 실패 ID: {failure_id}. 원래 질문과 자료는 유지하고 출력 계약만 보완하라.").message
        except ValidationError:
            return finish("repair_input_limit")
        event("repair_scheduled", failure_id=failure_id)
