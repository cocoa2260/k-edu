import os
from types import SimpleNamespace

import httpx
from fastapi.testclient import TestClient


from app.main import create_app  # noqa: E402
from app.providers.errors import (  # noqa: E402
    ProviderConnectionError,
    ProviderResponseError,
    ProviderTimeoutError,
)


class MockProvider:
    provider_name = "mock"
    model_name = "fixed-test-model"

    def generate(self, message: str) -> str:
        return f"테스트 응답: {message}"


def test_contract_is_independent_of_real_api():
    with TestClient(create_app(MockProvider())) as client:
        res = client.post("/ai/chat", json={"message": "회의 일정 정리"})
    assert res.status_code == 200
    assert res.json() == {
        "provider": "mock",
        "model": "fixed-test-model",
        "answer": "테스트 응답: 회의 일정 정리",
    }


def test_input_validation_prevents_provider_call():
    class ExplodingProvider(MockProvider):
        def generate(self, message: str) -> str:
            raise AssertionError("Provider는 호출되면 안 됩니다")

    with TestClient(create_app(ExplodingProvider())) as client:
        res = client.post("/ai/chat", json={"message": "   "})
    assert res.status_code == 422


def test_health_does_not_call_model():
    with TestClient(create_app(MockProvider())) as client:
        res = client.get("/health")
    assert res.json() == {
        "status": "ok",
        "provider": "mock",
        "model": "fixed-test-model",
    }


def test_provider_errors_have_stable_http_mapping():
    errors = [
        (ProviderConnectionError(), 503),
        (ProviderTimeoutError(), 504),
        (ProviderResponseError(), 502),
    ]
    for error, expected_status in errors:
        class BrokenProvider(MockProvider):
            def generate(self, message: str) -> str:
                raise error

        with TestClient(create_app(BrokenProvider())) as client:
            res = client.post("/ai/chat", json={"message": "확인"})
        assert res.status_code == expected_status
        assert "Traceback" not in res.text


def test_factory_selects_only_configured_provider(monkeypatch):
    from app.providers.factory import create_provider

    monkeypatch.setenv("AI_PROVIDER", "ollama")
    monkeypatch.setenv("OLLAMA_MODEL", "course-local")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    provider = create_provider()
    assert provider.provider_name == "ollama"
    assert provider.model_name == "course-local"

    monkeypatch.setenv("AI_PROVIDER", "unsupported")
    try:
        create_provider()
    except RuntimeError:
        pass
    else:
        raise AssertionError("지원하지 않는 Provider를 수락했습니다")


def test_ollama_provider_parses_response_without_network(monkeypatch):
    from app.providers.ollama_provider import OllamaProvider

    monkeypatch.setenv("OLLAMA_MODEL", "test-model")

    def fake_post(url, *, json, timeout):
        assert url.endswith("/api/chat")
        assert json["model"] == "test-model"
        assert json["stream"] is False
        assert json["messages"][0]["content"] == "기록 확인"
        return httpx.Response(
            200,
            json={"message": {"content": "정상 생성"}},
            request=httpx.Request("POST", url),
        )

    monkeypatch.setattr(httpx, "post", fake_post)
    assert OllamaProvider().generate("기록 확인") == "정상 생성"


def test_openai_provider_uses_same_interface_without_network(monkeypatch):
    from app.providers import openai_provider

    class FakeResponses:
        def create(self, *, model, input):
            assert model == "course-cloud-model"
            assert input == "기록 확인"
            return SimpleNamespace(output_text="Cloud 테스트 응답")

    class FakeClient:
        responses = FakeResponses()

    monkeypatch.setenv("OPENAI_API_KEY", "unit-test-key")
    monkeypatch.setenv("OPENAI_MODEL", "course-cloud-model")
    monkeypatch.setattr(
        openai_provider, "OpenAI", lambda **kwargs: FakeClient()
    )
    provider = openai_provider.OpenAIProvider()
    assert provider.provider_name == "openai"
    assert provider.generate("기록 확인") == "Cloud 테스트 응답"
