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

    ENV = os.getenv("ENV", "development")

    # Comma-separated in .env, e.g: ALLOWED_ORIGINS=https://app.example.com,https://admin.example.com
    ALLOWED_ORIGINS = [
        origin.strip()
        for origin in os.getenv("ALLOWED_ORIGINS", "").split(",")
        if origin.strip()
    ]


settings = Settings()


def _validate_settings():
    """
    Fail fast and loudly at startup rather than running with an insecure or
    broken configuration. A missing DB_URL or SECRET_KEY (or a SECRET_KEY
    that's just the placeholder from .env.example) would otherwise only
    surface later as a confusing runtime error - or worse, run "successfully"
    with a guessable/default secret in production.
    """
    if not settings.DB_URL:
        raise RuntimeError("DB_URL is not set. Copy .env.example to .env and configure it.")

    if not settings.SECRET_KEY:
        raise RuntimeError("SECRET_KEY is not set. Copy .env.example to .env and configure it.")

    if settings.ENV == "production":
        if settings.SECRET_KEY in ("my_super_secret_key_123", "changeme", "secret"):
            raise RuntimeError(
                "SECRET_KEY is still set to a known placeholder value. "
                "Generate a real one: python -c \"import secrets; print(secrets.token_hex(32))\""
            )
        if len(settings.SECRET_KEY) < 32:
            raise RuntimeError("SECRET_KEY is too short for production (need 32+ characters).")
        if not settings.ALLOWED_ORIGINS:
            raise RuntimeError("ALLOWED_ORIGINS must be set when ENV=production (no wildcard CORS in prod).")


_validate_settings()
