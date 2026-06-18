from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Blog Platform API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    DATABASE_URL: str = "sqlite:///./data/blog.db"

    SECRET_KEY: str = "change-me-in-production-super-secret-key-32bytes"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
