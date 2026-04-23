import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./tpu_pet.db")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
    JWT_EXPIRE_DAYS: int = int(os.getenv("JWT_EXPIRE_DAYS", "7"))
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "local")
    LLM_API_URL: str = os.getenv("LLM_API_URL", "http://localhost:11434/api/generate")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "qwen2.5:7b")
    LLM_TIMEOUT: int = int(os.getenv("LLM_TIMEOUT", "60"))


settings = Settings()
