from typing import Annotated, Optional
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field


class ContactoBase(SQLModel):
    """Campos compartidos para Contacto."""
    nombre_completo: Annotated[str, Field(max_length=150, nullable=False)]
    email: Annotated[str, Field(index=True, max_length=150, nullable=False)]
    telefono: Annotated[Optional[str], Field(default=None, max_length=50)]
    tipo_mensaje: Annotated[str, Field(default="consulta_general", max_length=50)]
    mensaje: Annotated[str, Field(nullable=False)]
    leido: Annotated[bool, Field(default=False)]


class Contacto(ContactoBase, table=True):
    """Modelo de base de datos para la tabla 'contactos'."""
    __tablename__ = "contactos"

    id: Annotated[Optional[int], Field(default=None, primary_key=True)]
    created_at: Annotated[datetime, Field(default_factory=lambda: datetime.now(timezone.utc))]


class ContactoPublic(ContactoBase):
    """Esquema de respuesta pública para Contacto."""
    id: int
    created_at: datetime


class ContactoCreate(ContactoBase):
    """Esquema para crear Contacto."""
    pass


class ContactoUpdate(SQLModel):
    """Esquema para actualizar Contacto."""
    nombre_completo: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    tipo_mensaje: Optional[str] = None
    mensaje: Optional[str] = None
    leido: Optional[bool] = None
