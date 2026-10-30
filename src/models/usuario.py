from typing import Annotated, Optional, TYPE_CHECKING
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from src.models.emprendedor import Emprendedor, EmprendedorPublic


class UsuarioBase(SQLModel):
    """Campos compartidos para Usuario."""
    email: Annotated[str, Field(unique=True, index=True, max_length=150, nullable=False)]
    nombre_completo: Annotated[str, Field(max_length=150, nullable=False)]
    rol: Annotated[str, Field(default="cliente", max_length=20, nullable=False)]
    activo: Annotated[bool, Field(default=True)]


class Usuario(UsuarioBase, table=True):
    """Modelo de base de datos para la tabla 'usuarios'."""
    __tablename__ = "usuarios"

    id: Annotated[Optional[int], Field(default=None, primary_key=True)]
    password_hash: Annotated[str, Field(nullable=False)]
    created_at: Annotated[datetime, Field(default_factory=lambda: datetime.now(timezone.utc))]

    # Relación uno-a-uno con Emprendedor
    emprendedor: Optional["Emprendedor"] = Relationship(back_populates="usuario")


class UsuarioPublic(UsuarioBase):
    """Esquema de respuesta pública para Usuario."""
    id: int
    created_at: datetime


class UsuarioPublicNested(UsuarioPublic):
    """Esquema anidado (Nested) con información de perfil de Emprendedor."""
    emprendedor: Optional["EmprendedorPublic"] = None


class UsuarioCreate(UsuarioBase):
    """Esquema para crear Usuario."""
    password: str = Field(min_length=4)


class UsuarioUpdate(SQLModel):
    """Esquema para actualizar Usuario."""
    nombre_completo: Optional[str] = Field(default=None, min_length=1, max_length=150)
    password: Optional[str] = Field(default=None, min_length=4)
    rol: Optional[str] = Field(default=None, regex=r"^(cliente|emprendedor|admin)$")
    activo: Optional[bool] = None


