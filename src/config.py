import os

from pydantic_settings import BaseSettings
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()


class DBSettings(BaseModel):

    DB_NAME: str = os.getenv("DB_NAME")
    DB_USER: str = os.getenv("DB_USER")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD")
    DB_HOST: str = os.getenv("DB_HOST")
    DB_PORT: int = os.getenv("DB_PORT")

    url: str = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    echo: bool = False

    REDIS_HOST: str = os.getenv("REDIS_HOST")
    REDIS_PORT: int = os.getenv("REDIS_PORT")


class Settings(BaseSettings):

    db: DBSettings = DBSettings()

    SENDGRID_API_KEY: str = os.getenv("SENDGRID_API_KEY")
    DEFAULT_FROM_EMAIL: str = os.getenv("DEFAULT_FROM_EMAIL")
    PASSWORD_RESET_TEMPLATE_ID: str = os.getenv("PASSWORD_RESET_TEMPLATE_ID")
    REGISTRATION_CONFIRMATION_TEMPLATE_ID: str = os.getenv("REGISTRATION_CONFIRMATION_TEMPLATE_ID")


settings = Settings()
