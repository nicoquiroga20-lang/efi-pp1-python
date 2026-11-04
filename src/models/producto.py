from typing import Annotated, Optional, TYPE_CHECKING
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from src.models.emprendedor import Emprendedor, EmprendedorPublic
    from src.models.categoria import Categoria, CategoriaPublic


class ProductoBase(SQLModel):
    """Campos compartidos para Producto."""
    categoria_id: Annotated[int, Field(foreign_key="categorias.id", nullable=False)]
    nombre: Annotated[str, Field(index=True, max_length=150, nullable=False)]
    descripcion: Annotated[Optional[str], Field(default=None, max_length=500)]
    precio: Annotated[float, Field(ge=0.0, nullable=False)]
    imagen_url: Annotated[Optional[str], Field(default=None, max_length=255)]
    en_stock: Annotated[bool, Field(default=True)]
    destacado: Annotated[bool, Field(default=False)]
    activo: Annotated[bool, Field(default=True)]


class Producto(ProductoBase, table=True):
    """Modelo de base de datos para la tabla 'productos'."""
    __tablename__ = "productos"

    id: Annotated[Optional[int], Field(default=None, primary_key=True)]
    emprendedor_id: Annotated[int, Field(foreign_key="emprendedores.id", nullable=False)]
    created_at: Annotated[datetime, Field(default_factory=lambda: datetime.now(timezone.utc))]

    # Relaciones relacionales
    emprendedor: Optional["Emprendedor"] = Relationship(back_populates="productos")
    categoria: Optional["Categoria"] = Relationship(back_populates="productos")


class ProductoPublic(ProductoBase):
    """Esquema de respuesta pública para Producto."""
    id: int
    emprendedor_id: int
    created_at: datetime


class ProductoPublicNested(ProductoPublic):
    """Esquema anidado (Nested) con información de Categoria y Emprendedor."""
    categoria: Optional["CategoriaPublic"] = None
    emprendedor: Optional["EmprendedorPublic"] = None


class ProductoCreate(ProductoBase):
    """Esquema para crear Producto."""
    emprendedor_id: int


class ProductoUpdate(SQLModel):
    """Esquema para actualizar Producto."""
    emprendedor_id: int = Field(default=None, gt=0)
    categoria_id: int = Field(default=None, gt=0)
    nombre: str = Field(default=None, min_length=1, max_length=150)
    descripcion: Optional[str] = Field(default=None, max_length=500)
    precio: float = Field(default=None, ge=0.0)
    imagen_url: Optional[str] = Field(default=None, max_length=255)
    en_stock: bool = None
    destacado: bool = None
    activo: bool = None

