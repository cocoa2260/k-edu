from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class AISettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AI_")
    provider: str = "fake"
    api_key: SecretStr = SecretStr("not-used-for-fake")

settings = AISettings()
print(settings)
print("raw key access is explicit:", settings.api_key.get_secret_value()[:3])
