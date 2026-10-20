from typing import Annotated, List, Optional, TYPE_CHECKING
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Relationship

from src.models.rubro import RubroPublic
from src.models.feria import FeriaPublic
from src.models.plan import PlanPublic

if TYPE_CHECKING:
    from src.models.usuario import Usuario
    from src.models.rubro import Rubro
    from src.models.feria import Feria
    from src.models.plan import Plan
    from src.models.producto import Producto


class EmprendedorBase(SQLModel):
    """Campos compartidos para Emprendedor."""
    nombre_fantasia: Annotated[str, Field(index=True, max_length=150, nullable=False)]
    descripcion_bio: Annotated[Optional[str], Field(default=None, max_length=500)]
    telefono_whatsapp: Annotated[str, Field(max_length=30, nullable=False)]
    instagram: Annotated[Optional[str], Field(default=None, max_length=100)]
    numero_puesto: Annotated[Optional[str], Field(default=None, max_length=50)]
    logo_url: Annotated[Optional[str], Field(default=None, max_length=255)]
    banner_url: Annotated[Optional[str], Field(default=None, max_length=255)]
    rubro_id: Annotated[int, Field(foreign_key="rubros.id", nullable=False)]
    feria_id: Annotated[Optional[int], Field(default=None, foreign_key="ferias.id")]
    plan_id: Annotated[int, Field(default=1, foreign_key="planes.id", nullable=False)]
    destacado: Annotated[bool, Field(default=False)]
    activo: Annotated[bool, Field(default=True)]


class Emprendedor(EmprendedorBase, table=True):
    """Modelo de base de datos para la tabla 'emprendedores'."""
    __tablename__ = "emprendedores"

    id: Annotated[Optional[int], Field(default=None, primary_key=True)]
    usuario_id: Annotated[int, Field(foreign_key="usuarios.id", unique=True, nullable=False)]
    created_at: Annotated[datetime, Field(default_factory=lambda: datetime.now(timezone.utc))]

    # Relaciones relacionales
    usuario: Optional["Usuario"] = Relationship(back_populates="emprendedor")
    rubro: Optional["Rubro"] = Relationship(back_populates="emprendedores")
    feria: Optional["Feria"] = Relationship(back_populates="emprendedores")
    plan: Optional["Plan"] = Relationship(back_populates="emprendedores")
    productos: List["Producto"] = Relationship(back_populates="emprendedor")


class EmprendedorPublic(EmprendedorBase):
    """Esquema de respuesta pública para Emprendedor."""
    id: int
    usuario_id: int
    created_at: datetime


class EmprendedorPublicNested(EmprendedorPublic):
    """Esquema anidado (Nested) con información de relaciones."""
    rubro: Optional[RubroPublic] = None
    feria: Optional[FeriaPublic] = None
    plan: Optional[PlanPublic] = None


class EmprendedorCreate(EmprendedorBase):
    """Esquema para crear Emprendedor."""
    usuario_id: int


class EmprendedorUpdate(SQLModel):
    """Esquema para actualizar Emprendedor."""
    nombre_fantasia: Optional[str] = None
    descripcion_bio: Optional[str] = None
    telefono_whatsapp: Optional[str] = None
    instagram: Optional[str] = None
    numero_puesto: Optional[str] = None
    logo_url: Optional[str] = None
    banner_url: Optional[str] = None
    rubro_id: Optional[int] = None
    feria_id: Optional[int] = None
    plan_id: Optional[int] = None
    destacado: Optional[bool] = None
    activo: Optional[bool] = None
