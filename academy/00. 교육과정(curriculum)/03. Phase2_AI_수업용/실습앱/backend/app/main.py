"""기본 Chat 시작본. 뒤 단원의 RAG/Agent API는 아직 없습니다."""
import os
from typing import Literal
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ValidationError
from app.experiments import prepare
from app.providers.base import AIProvider
from app.providers.errors import (
    ProviderConnectionError, ProviderResponseError, ProviderTimeoutError, ProviderUpstreamError,
)
from app.providers.factory import create_provider
from app.schemas import ChatRequest, ChatResponse
from app.service import AIService


class PrepareRequest(BaseModel):
    case_id: str
    variant: Literal['baseline','instruction','one_shot','few_shot','focused']


def create_app(provider: AIProvider | None = None) -> FastAPI:
    selected = provider if provider is not None else create_provider()
    service=AIService(selected)
    api=FastAPI(title='AI 문서 도우미 - 기본 Chat 시작본')
    origins=os.getenv('FRONTEND_ORIGINS','http://localhost:5173,http://127.0.0.1:5173')
    api.add_middleware(CORSMiddleware,allow_origins=[x.strip().rstrip('/') for x in origins.split(',') if x.strip()],
                       allow_credentials=False,allow_methods=['GET','POST'],allow_headers=['Content-Type'])

    @api.get('/health')
    def health() -> dict[str,str]:
        # 실제 모델 호출이 아닌 설정 확인
        return {'status':'ok','provider':selected.provider_name,'model':selected.model_name}

    @api.post('/ai/chat',response_model=ChatResponse)
    def chat(request:ChatRequest) -> ChatResponse:
        try:
            result=service.chat(request.message)
        except ProviderConnectionError as exc:
            raise HTTPException(503,'AI Provider 연결 실패') from exc
        except ProviderTimeoutError as exc:
            raise HTTPException(504,'AI Provider 응답 시간 초과') from exc
        except (ProviderUpstreamError,ProviderResponseError) as exc:
            raise HTTPException(502,'AI Provider 응답 오류') from exc
        return ChatResponse(provider=result.provider,model=result.model,answer=result.answer)

    @api.post('/ai/prepare')
    def prepare_experiment(request:PrepareRequest) -> dict:
        try:
            return prepare(request.case_id,request.variant)
        except ValidationError as exc:
            raise HTTPException(422,'질문 또는 준비 입력의 문자 제한을 확인하세요') from exc
        except ValueError as exc:
            raise HTTPException(422,'알 수 없는 실험 사례 또는 조건입니다') from exc
    return api


# 실행: python -m uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000
