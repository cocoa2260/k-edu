import os

from dotenv import load_dotenv


load_dotenv()


def required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value or value.startswith("<"):
        raise RuntimeError(f"설정이 필요합니다: {name}")
    return value
