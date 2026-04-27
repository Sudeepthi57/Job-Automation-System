from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    database_url: str = "sqlite+aiosqlite:///./jobs.db"

    min_relevance_score: int = 6  # Jobs below this score are filtered out

    target_role: str = "AI Engineer"
    target_skills: str = "Python, FastAPI, LLM, Machine Learning, Backend"

    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
