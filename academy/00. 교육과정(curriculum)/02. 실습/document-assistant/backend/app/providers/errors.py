class AIProviderError(Exception):
    """외부 AI 호출에서 생긴 예외의 공통 부모 클래스."""


class ProviderConnectionError(AIProviderError):
    """Provider에 연결할 수 없음."""


class ProviderTimeoutError(AIProviderError):
    """Provider 응답 대기 시간 초과."""


class ProviderUpstreamError(AIProviderError):
    """Provider가 오류 상태를 반환함."""


class ProviderResponseError(AIProviderError):
    """성공 응답이라도 필요한 내용이 없거나 형식이 잘못됨."""
