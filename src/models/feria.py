from typing import Annotated, List, Optional, TYPE_CHECKING
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from src.models.emprendedor import Emprendedor, EmprendedorPublic


class FeriaBase(SQLModel):
    """Campos compartidos para Feria."""
    nombre: Annotated[str, Field(index=True, min_length=1, max_length=150, nullable=False)]
    ubicacion: Annotated[str, Field(min_length=1, max_length=255, nullable=False)]
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


class FeriaPublicNested(FeriaPublic):
    """Esquema anidado (Nested) con información de emprendedores."""
    emprendedores: List["EmprendedorPublic"] = []


class FeriaCreate(FeriaBase):
    """Esquema para crear Feria."""
    pass


class FeriaUpdate(SQLModel):
    """Esquema para actualizar Feria."""
    nombre: Optional[str] = Field(default=None, min_length=1, max_length=150)
    ubicacion: Optional[str] = Field(default=None, min_length=1, max_length=255)
    proxima_fecha: Optional[datetime] = None
    horario: Optional[str] = Field(default=None, max_length=100)
    descripcion: Optional[str] = Field(default=None, max_length=500)
    activa: Optional[bool] = None


