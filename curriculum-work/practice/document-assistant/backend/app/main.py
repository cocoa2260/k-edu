import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException

from app.providers.base import AIProvider
from app.providers.errors import (
    ProviderConnectionError,
    ProviderResponseError,
    ProviderTimeoutError,
    ProviderUpstreamError,
)
from app.providers.factory import create_provider
from app.schemas import ChatRequest, ChatResponse
from app.service import AIService


def create_app(provider: AIProvider | None = None) -> FastAPI:
    # 테스트에서는 Mock을 주입하고, 일반 실행에서는 Factory를 사용합니다.
    selected = provider if provider is not None else create_provider()
    service = AIService(selected)
    api = FastAPI(title="AI Provider Abstraction")

    raw_origins = os.getenv(
        "FRONTEND_ORIGINS", "http://localhost:5173"
    )
    allowed_origins = [
        origin.strip().rstrip("/")
        for origin in raw_origins.split(",")
        if origin.strip()
    ]

    api.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )

    @api.get("/health")
    def health() -> dict[str, str]:
        return {
            "status": "ok",
            "provider": selected.provider_name,
            "model": selected.model_name,
        }

    @api.post("/ai/chat", response_model=ChatResponse)
    def chat(request: ChatRequest) -> ChatResponse:
        try:
            result = service.chat(request.message)
        except ProviderConnectionError as exc:
            raise HTTPException(503, "AI Provider 연결 실패") from exc
        except ProviderTimeoutError as exc:
            raise HTTPException(504, "AI Provider 응답 시간 초과") from exc
        except (ProviderUpstreamError, ProviderResponseError) as exc:
            raise HTTPException(502, "AI Provider 응답 오류") from exc

        return ChatResponse(
            provider=result.provider,
            model=result.model,
            answer=result.answer,
        )

    return api


# Launch with uvicorn app.main:create_app --factory to avoid import-time configuration.
