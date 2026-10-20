from typing import Generator
from sqlmodel import Session, create_engine
from src.core.config import settings

# En SQLite se requiere check_same_thread=False para permitir múltiples hilos en FastAPI
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    connect_args=connect_args,
)


def get_session() -> Generator[Session, None, None]:
    """
    Generador de sesión de base de datos para inyección de dependencias en FastAPI.
    Asegura que cada solicitud HTTP maneje su propia sesión y se cierre al terminar.
    """
    with Session(engine) as session:
        yield session
