from pathlib import Path

from alembic import command
from alembic.config import Config


def init_db() -> None:
    """Aplica las migraciones pendientes antes de aceptar solicitudes."""
    config = Config(str(Path(__file__).resolve().parents[2] / "alembic.ini"))
    config.attributes["configure_logger"] = False
    command.upgrade(config, "head")
