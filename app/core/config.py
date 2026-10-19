from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    APP_NAME = os.getenv("APP_NAME", "Tennis Backend")
    APP_VERSION = os.getenv("APP_VERSION", "1.0.0")

    DB_URL = os.getenv("DB_URL")

    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60)
    )
    REFRESH_TOKEN_EXPIRE_DAYS = int(
        os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7)
    )

    # Email
    EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
    EMAIL_PORT = int(os.getenv("EMAIL_PORT", 465))
    EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    EMAIL_FROM_NAME = os.getenv(
        "EMAIL_FROM_NAME",
        "Final Whistle"
    )

    ENV = os.getenv("ENV", "development")

    ALLOWED_ORIGINS = [
        origin.strip()
        for origin in os.getenv("ALLOWED_ORIGINS", "").split(",")
        if origin.strip()
    ]


settings = Settings()
