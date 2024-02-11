from pydantic import BaseSettings, EmailStr


class Settings(BaseSettings):
    app_title: str = "Заголовок будет позже"
    description: str = "Описание будет позже"
    database_url: str = "sqlite+aiosqlite:///./fastapi.db"
    secret: str = "SECRET"
    first_superuser_email: EmailStr | None
    first_superuser_password: str | None
    type: str | None
    project_id: str | None
    private_key_id: str | None
    private_key: str | None
    client_email: str | None
    client_id: str | None
    auth_uri: str | None
    token_uri: str | None
    auth_provider_x509_cert_url: str | None
    client_x509_cert_url: str | None
    universe_domain: str | None
    email: str | None

    class Config:
        env_file = ".env"


settings = Settings()
