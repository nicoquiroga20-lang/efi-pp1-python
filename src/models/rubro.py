from typing import Annotated, List, Optional, TYPE_CHECKING
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from src.models.emprendedor import Emprendedor, EmprendedorPublic


class RubroBase(SQLModel):
    """Campos compartidos para Rubro."""
    nombre: Annotated[str, Field(unique=True, index=True, min_length=1, max_length=100, nullable=False)]
    descripcion: Annotated[Optional[str], Field(default=None, max_length=255)]
    activo: Annotated[bool, Field(default=True)]


class Rubro(RubroBase, table=True):
    """Modelo de base de datos para la tabla 'rubros'."""
    __tablename__ = "rubros"

    id: Annotated[Optional[int], Field(default=None, primary_key=True)]
    created_at: Annotated[datetime, Field(default_factory=lambda: datetime.now(timezone.utc))]

    # Relación uno-a-muchos con Emprendedor
    emprendedores: List["Emprendedor"] = Relationship(back_populates="rubro")


class RubroPublic(RubroBase):
    """Esquema de respuesta pública para Rubro."""
    id: int
    created_at: datetime


class RubroPublicNested(RubroPublic):
    """Esquema anidado (Nested) con información de emprendedores."""
    emprendedores: List["EmprendedorPublic"] = []


class RubroCreate(RubroBase):
    """Esquema para crear Rubro."""
    pass


class RubroUpdate(SQLModel):
    """Esquema para actualizar Rubro."""
    nombre: str = Field(default=None, min_length=1, max_length=100)
    descripcion: Optional[str] = Field(default=None, max_length=255)
    activo: bool = None


