from typing import Generator
from sqlmodel import Session, create_engine
from src.core.config import settings

from sqlalchemy import event
from sqlite3 import Connection as SQLite3Connection

# En SQLite se requiere check_same_thread=False para permitir múltiples hilos en FastAPI
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    connect_args=connect_args,
)

if settings.DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        if isinstance(dbapi_connection, SQLite3Connection):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()


def get_session() -> Generator[Session, None, None]:
    """
    Generador de sesión de base de datos para inyección de dependencias en FastAPI
    Asegura que cada solicitud HTTP maneje su propia sesión y se cierre al terminar
    """
    with Session(engine) as session:
        yield session
