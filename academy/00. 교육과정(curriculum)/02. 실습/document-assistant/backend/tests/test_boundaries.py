import os
import subprocess
import sys
from types import SimpleNamespace

import httpx
import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.providers.errors import ProviderResponseError, ProviderUpstreamError
from app.providers.factory import create_provider
from app.providers.ollama_provider import OllamaProvider


class RecordingProvider:
    provider_name = "contract-test"
    model_name = "not-a-real-model"

    def __init__(self):
        self.calls = []

    def generate(self, message):
        self.calls.append(message)
        return "fixed contract response"


@pytest.mark.parametrize("payload", [{}, {"message": ""}, {"message": "  "}, {"message": "x" * 2001}, {"message": None}, {"message": 12}, {"message": []}])
def test_invalid_input_never_reaches_provider(payload):
    provider = RecordingProvider()
    with TestClient(create_app(provider)) as client:
        response = client.post("/ai/chat", json=payload)
    assert response.status_code == 422
    assert provider.calls == []


def test_trim_and_unknown_provider_field_preserve_original_contract():
    provider = RecordingProvider()
    with TestClient(create_app(provider)) as client:
        response = client.post("/ai/chat", json={"message": "  확인  ", "provider": "openai", "model": "client-model"})
    assert provider.calls == ["확인"]
    assert response.json() == {"provider": "contract-test", "model": "not-a-real-model", "answer": "fixed contract response"}


def test_maximum_length_is_accepted():
    provider = RecordingProvider()
    with TestClient(create_app(provider)) as client:
        response = client.post("/ai/chat", json={"message": "x" * 2000})
    assert response.status_code == 200
    assert len(provider.calls[0]) == 2000


def test_disallowed_origin_preflight_is_not_allowed():
    with TestClient(create_app(RecordingProvider())) as client:
        response = client.options("/ai/chat", headers={"Origin": "http://unlisted.invalid", "Access-Control-Request-Method": "POST"})
    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers


def test_cors_does_not_authenticate_an_actual_post():
    provider = RecordingProvider()
    with TestClient(create_app(provider)) as client:
        response = client.post("/ai/chat", json={"message": "確認"}, headers={"Origin": "http://unlisted.invalid"})
    assert response.status_code == 200
    assert len(provider.calls) == 1
    assert "access-control-allow-origin" not in response.headers


def test_upstream_details_are_not_exposed():
    class Broken(RecordingProvider):
        def generate(self, message):
            raise ProviderUpstreamError("private upstream detail")

    with TestClient(create_app(Broken())) as client:
        response = client.post("/ai/chat", json={"message": "確認"})
    assert response.status_code == 502
    assert "private upstream detail" not in response.text


@pytest.mark.parametrize("content", [None, 123, [], "", "   "])
def test_invalid_ollama_content_is_rejected(monkeypatch, content):
    monkeypatch.setattr(httpx, "post", lambda *a, **k: httpx.Response(200, json={"message": {"content": content}}, request=httpx.Request("POST", "http://test.invalid/api/chat")))
    with pytest.raises(ProviderResponseError):
        OllamaProvider().generate("sample")


def test_invalid_ollama_json_is_rejected(monkeypatch):
    monkeypatch.setattr(httpx, "post", lambda *a, **k: httpx.Response(200, text="not json", request=httpx.Request("POST", "http://test.invalid/api/chat")))
    with pytest.raises(ProviderResponseError):
        OllamaProvider().generate("sample")


def test_selected_provider_requires_its_own_configuration(monkeypatch):
    monkeypatch.delenv("OLLAMA_MODEL", raising=False)
    with pytest.raises(RuntimeError, match="OLLAMA_MODEL"):
        create_provider()
    monkeypatch.setenv("AI_PROVIDER", "openai")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        create_provider()


def test_import_has_no_provider_configuration_side_effect():
    env = os.environ.copy()
    for name in ["AI_PROVIDER", "OLLAMA_MODEL", "OPENAI_API_KEY", "OPENAI_MODEL"]:
        env.pop(name, None)
    code = "import sys; import app.main; assert 'app.providers.openai_provider' not in sys.modules"
    result = subprocess.run([sys.executable, "-c", code], env=env, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr

