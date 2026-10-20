from typing import Annotated, List, Optional, TYPE_CHECKING
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from src.models.emprendedor import Emprendedor


class FeriaBase(SQLModel):
    """Campos compartidos para Feria."""
    nombre: Annotated[str, Field(index=True, max_length=150, nullable=False)]
    ubicacion: Annotated[str, Field(max_length=255, nullable=False)]
    proxima_fecha: Annotated[Optional[datetime], Field(default=None)]
    horario: Annotated[Optional[str], Field(default=None, max_length=100)]
    descripcion: Annotated[Optional[str], Field(default=None, max_length=500)]
    activa: Annotated[bool, Field(default=True)]


class Feria(FeriaBase, table=True):
    """Modelo de base de datos para la tabla 'ferias'."""
    __tablename__ = "ferias"

    id: Annotated[Optional[int], Field(default=None, primary_key=True)]
    created_at: Annotated[datetime, Field(default_factory=lambda: datetime.now(timezone.utc))]

    # Relación uno-a-muchos con Emprendedor
    emprendedores: List["Emprendedor"] = Relationship(back_populates="feria")


class FeriaPublic(FeriaBase):
    """Esquema de respuesta pública para Feria."""
    id: int
    created_at: datetime


class FeriaCreate(FeriaBase):
    """Esquema para crear Feria."""
    pass


class FeriaUpdate(SQLModel):
    """Esquema para actualizar Feria."""
    nombre: Optional[str] = None
    ubicacion: Optional[str] = None
    proxima_fecha: Optional[datetime] = None
    horario: Optional[str] = None
    descripcion: Optional[str] = None
    activa: Optional[bool] = None
