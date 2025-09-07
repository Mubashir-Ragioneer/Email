# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "Email Microservice"
    ENV: str = "dev"

    # smtp
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    FROM_EMAIL: str = "no-reply@example.com"
    FROM_NAME: str = "My App"

    # mongodb
    MONGO_URI: str = "mongodb+srv://mubashir:dxarmy786@cluster1.gpnksf7.mongodb.net/emaildb"
    # add if missing
    PUBLIC_BASE_URL: str = "http://127.0.0.1:8000"
    GOOGLE_CLIENT_SECRET_FILE: str = "secrets/client_secret.json"
    GOOGLE_TOKEN_FILE: str = "secrets/token.json"


    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

settings = Settings()
