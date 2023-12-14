import os
from datetime import datetime, timedelta
from pathlib import Path

from pydantic_settings import BaseSettings
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).parent.parent


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


class AuthJWT(BaseModel):

    private_key_path: Path = BASE_DIR / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    access_token_expire: datetime = timedelta(minutes=15)
    refresh_token_expire: datetime = timedelta(days=7)


class Settings(BaseSettings):

    db: DBSettings = DBSettings()
    auth_jwt: AuthJWT = AuthJWT()

    current_host: str = "https://0cd6-91-211-120-11.ngrok-free.app"

    NOVA_POSTA_KEY: str = os.getenv("NOVA_POSTA_KEY")

    LIQPAY_PUBLIC_KEY: str = os.getenv("LIQPAY_PUBLIC_KEY")
    LIQPAY_PRIVATE_KEY: str = os.getenv("LIQPAY_PRIVATE_KEY")

    SENDGRID_API_KEY: str = os.getenv("SENDGRID_API_KEY")
    DEFAULT_FROM_EMAIL: str = os.getenv("DEFAULT_FROM_EMAIL")
    PASSWORD_RESET_TEMPLATE_ID: str = os.getenv("PASSWORD_RESET_TEMPLATE_ID")
    REGISTRATION_CONFIRMATION_TEMPLATE_ID: str = os.getenv("REGISTRATION_CONFIRMATION_TEMPLATE_ID")


settings = Settings()
