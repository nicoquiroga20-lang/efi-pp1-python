from typing import Annotated, List, Optional, TYPE_CHECKING
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from src.models.producto import Producto, ProductoPublic


class CategoriaBase(SQLModel):
    """Campos compartidos para Categoria."""
    nombre: Annotated[str, Field(index=True, min_length=1, max_length=100, nullable=False)]
    descripcion: Annotated[Optional[str], Field(default=None, max_length=255)]
    activo: Annotated[bool, Field(default=True)]


class Categoria(CategoriaBase, table=True):
    """Modelo de base de datos para la tabla 'categorias'."""
    __tablename__ = "categorias"

    id: Annotated[Optional[int], Field(default=None, primary_key=True)]
    created_at: Annotated[datetime, Field(default_factory=lambda: datetime.now(timezone.utc))]

    # Relación uno-a-muchos con Producto
    productos: List["Producto"] = Relationship(back_populates="categoria")


class CategoriaPublic(CategoriaBase):
    """Esquema de respuesta pública para Categoria."""
    id: int
    created_at: datetime


class CategoriaPublicNested(CategoriaPublic):
    """Esquema anidado (Nested) con información de productos."""
    productos: List["ProductoPublic"] = []


class CategoriaCreate(CategoriaBase):
    """Esquema para crear Categoria."""
    pass


class CategoriaUpdate(SQLModel):
    """Esquema para actualizar Categoria."""
    nombre: str = Field(default=None, min_length=1, max_length=100)
    descripcion: Optional[str] = Field(default=None, max_length=255)
    activo: bool = None


