from typing import Annotated, List, Optional, TYPE_CHECKING
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from src.models.emprendedor import Emprendedor


class PlanBase(SQLModel):
    """Campos compartidos para Plan."""
    nombre: Annotated[str, Field(unique=True, index=True, max_length=100, nullable=False)]
    limite_productos: Annotated[int, Field(default=5, ge=1, nullable=False)]
    precio_mensual: Annotated[float, Field(default=0.0, ge=0.0, nullable=False)]
    permite_destacados: Annotated[bool, Field(default=False)]
    descripcion: Annotated[Optional[str], Field(default=None, max_length=255)]
    activo: Annotated[bool, Field(default=True)]


class Plan(PlanBase, table=True):
    """Modelo de base de datos para la tabla 'planes'."""
    __tablename__ = "planes"

    id: Annotated[Optional[int], Field(default=None, primary_key=True)]
    created_at: Annotated[datetime, Field(default_factory=lambda: datetime.now(timezone.utc))]

    # Relación uno-a-muchos con Emprendedor
    emprendedores: List["Emprendedor"] = Relationship(back_populates="plan")


class PlanPublic(PlanBase):
    """Esquema de respuesta pública para Plan."""
    id: int
    created_at: datetime


class PlanCreate(PlanBase):
    """Esquema para crear Plan."""
    pass


class PlanUpdate(SQLModel):
    """Esquema para actualizar Plan."""
    nombre: Optional[str] = None
    limite_productos: Optional[int] = None
    precio_mensual: Optional[float] = None
    permite_destacados: Optional[bool] = None
    descripcion: Optional[str] = None
    activo: Optional[bool] = None
