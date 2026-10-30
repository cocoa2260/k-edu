from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_")
    environment: str = "development"
    debug: bool = False

settings = Settings()
print(settings)
# APP_DEBUG=true python settings_env.py
