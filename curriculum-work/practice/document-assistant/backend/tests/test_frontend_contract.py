import os


from fastapi.testclient import TestClient  # noqa: E402
from app.main import create_app  # noqa: E402


class MockProvider:
    provider_name = "mock"
    model_name = "offline-model"

    def generate(self, message: str) -> str:
        return f"응답: {message}"


def test_frontend_post_contract():
    with TestClient(create_app(MockProvider())) as client:
        result = client.post(
            "/ai/chat",
            json={"message": "참가 안내 문구"},
            headers={"Origin": "http://localhost:5173"},
        )
    assert result.status_code == 200
    assert result.json() == {
        "provider": "mock",
        "model": "offline-model",
        "answer": "응답: 참가 안내 문구",
    }
    assert result.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_cors_preflight_allows_classroom_origin():
    with TestClient(create_app(MockProvider())) as client:
        result = client.options(
            "/ai/chat",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type",
            },
        )
    assert result.status_code == 200
    assert result.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_invalid_message_is_rejected_before_provider_call():
    class FailingIfCalled(MockProvider):
        def generate(self, message: str) -> str:
            raise AssertionError("Validation보다 Provider가 먼저 호출됐습니다")

    with TestClient(create_app(FailingIfCalled())) as client:
        result = client.post("/ai/chat", json={"message": "  "})
    assert result.status_code == 422
