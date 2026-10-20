from sqlmodel import SQLModel
from src.db.session import engine
# Se importan los modelos para que queden registrados en SQLModel.metadata
import src.models  # noqa: F401


def init_db() -> None:
    """
    Inicializa la base de datos creando las tablas que aún no existan.
    """
    SQLModel.metadata.create_all(engine)
