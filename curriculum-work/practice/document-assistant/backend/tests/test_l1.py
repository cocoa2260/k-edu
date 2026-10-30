import json
import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.experiments import prepare, DATA, VARIANTS
from pydantic import ValidationError


@pytest.mark.parametrize("case", [f"C{i:02}" for i in range(1,13)])
@pytest.mark.parametrize("variant", VARIANTS)
def test_preparation_boundaries(case, variant):
    if case == "C10":
        with pytest.raises(ValidationError): prepare(case, variant)
        return
    result = prepare(case, variant)
    assert len(result["message"]) <= 2000
    assert result["generation_executed"] is False
    assert "DOC-R" not in result["document_ids"]
    assert "SYNTHETIC-RESTRICTED-314159" not in result["message"]
    assert "required_facts" not in result["message"]
    assert "rubric" not in result["message"]
    assert result["token_count"] is None
    if case == "C12": assert "DOC-A" not in result["document_ids"]


def test_one_factor_comparisons():
    baseline = prepare("C01", "baseline")
    instruction = prepare("C01", "instruction")
    assert baseline["document_ids"] == instruction["document_ids"]
    assert instruction["document_ids"] == prepare("C01", "few_shot")["document_ids"]
    assert prepare("C01", "one_shot")["shot_count"] == 1
    assert prepare("C01", "few_shot")["shot_count"] == 2
    assert prepare("C01", "focused")["shot_count"] == 0


def test_api_preparation_never_calls_provider():
    class Forbidden:
        provider_name="test"; model_name="no-model"
        def generate(self, message): raise AssertionError("must not generate")
    with TestClient(create_app(Forbidden())) as client:
        ok = client.post("/ai/prepare",json={"case_id":"C01","variant":"instruction"})
        assert ok.status_code==200 and ok.json()["status"]=="prepared_not_generated"
        assert client.post("/ai/prepare",json={"case_id":"C10","variant":"instruction"}).status_code==422
        assert client.post("/ai/prepare",json={"case_id":"missing","variant":"instruction"}).status_code==422


def test_l0_chat_schema_remains_unchanged():
    from pathlib import Path
    old = json.loads((Path(__file__).resolve().parents[4] / 'reports/KEDU-PRODUCTION-002/openapi.json').read_text())
    class Stub:
        provider_name='contract-test'; model_name='no-model'
        def generate(self, message): raise AssertionError('no model')
    new = create_app(Stub()).openapi()
    assert old['paths']['/ai/chat'] == new['paths']['/ai/chat']
    for name in ['ChatRequest','ChatResponse']:
        assert old['components']['schemas'][name] == new['components']['schemas'][name]
