from typing import Optional
from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """
    Credenciales para inicio de sesión (POST /auth/login).
    """
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """
    Estructura de respuesta con token JWT de acceso.
    """
    access_token: str
    token_type: str = "bearer"
    rol: str
    usuario_id: int
    nombre_completo: str


class RegisterRequest(BaseModel):
    """
    Datos para registrar un nuevo usuario en el sistema.
    Permite elegir rol 'cliente' o 'emprendedor' en el registro.
    """
    email: EmailStr
    password: str
    nombre_completo: str
    rol: str = "cliente"  # 'cliente' o 'emprendedor'
    # Campos opcionales si se registra directamente como emprendedor:
    nombre_fantasia: Optional[str] = None
    telefono_whatsapp: Optional[str] = None
    rubro_id: Optional[int] = None
    feria_id: Optional[int] = None
