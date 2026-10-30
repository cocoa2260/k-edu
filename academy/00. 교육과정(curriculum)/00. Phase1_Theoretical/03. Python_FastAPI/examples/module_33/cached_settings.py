from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "AI Backend"

@lru_cache
def get_settings() -> Settings:
    return Settings()

print(get_settings() is get_settings())
