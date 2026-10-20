from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configuración global de la aplicación.
    Carga variables de entorno desde el archivo .env si existe.
    """
    PROJECT_NAME: str = "EFI API CRUD"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./database.db"
    BACKEND_CORS_ORIGINS: Union[str, List[str]] = ["*"]
    SECRET_KEY: str = "feria-imperio-super-secret-jwt-key-2026-vertex-solutions"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 horas

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.strip() == "*":
                return ["*"]
            if not v.startswith("["):
                return [i.strip() for i in v.split(",") if i.strip()]
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
