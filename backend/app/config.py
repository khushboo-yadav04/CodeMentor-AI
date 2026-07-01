from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    anthropic_api_key: str = ""
    use_mock_ai: bool = True
    judge0_url: str = "http://localhost:2358"
    database_url: str = "sqlite:///./codementor.db"
    secret_key: str = "dev-secret-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 10080

    class Config:
        env_file = ".env"


settings = Settings()
