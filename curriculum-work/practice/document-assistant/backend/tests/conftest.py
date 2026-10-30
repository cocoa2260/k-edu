"""Contract tests never call a real model service."""
import httpx
import pytest


@pytest.fixture(autouse=True)
def isolated_contract_environment(monkeypatch):
    monkeypatch.setenv("FRONTEND_ORIGINS", "http://localhost:5173")
    monkeypatch.setenv("AI_PROVIDER", "ollama")
    monkeypatch.setenv("OLLAMA_MODEL", "test-local-model")

    def no_network(*args, **kwargs):
        raise AssertionError("Real upstream HTTP is forbidden in contract tests")

    # Starlette TestClient uses its own in-process transport; real HTTP cannot escape.
    monkeypatch.setattr(httpx.HTTPTransport, "handle_request", no_network)

