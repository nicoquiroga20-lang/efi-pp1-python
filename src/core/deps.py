from typing import List, Callable, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select

from src.core.config import settings
from src.core.security import decode_access_token
from src.db.session import get_session
from src.models.usuario import Usuario
from src.models.emprendedor import Emprendedor

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/token"
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
) -> Usuario:
    """
    Obtiene y valida el usuario actual a partir del token JWT.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales de autenticación inválidas o expiradas",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if not payload:
        raise credentials_exception

    user_id_str: Optional[str] = payload.get("sub")
    if not user_id_str:
        raise credentials_exception

    try:
        user_id = int(user_id_str)
    except ValueError:
        raise credentials_exception

    user = session.get(Usuario, user_id)
    if not user:
        raise credentials_exception

    return user


def get_current_active_user(
    current_user: Usuario = Depends(get_current_user),
) -> Usuario:
    """
    Verifica que el usuario autenticado no esté deshabilitado.
    """
    if not current_user.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo en el sistema",
        )
    return current_user


def require_roles(allowed_roles: List[str]) -> Callable:
    """
    Factory de dependencias para control de acceso basado en roles (RBAC).
    Ejemplo: Depends(require_roles(["admin"]))
    """
    def role_checker(
        current_user: Usuario = Depends(get_current_active_user),
    ) -> Usuario:
        if current_user.rol not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permisos insuficientes. Rol requerido: {', '.join(allowed_roles)}",
            )
        return current_user

    return role_checker


def get_current_emprendedor(
    current_user: Usuario = Depends(require_roles(["emprendedor", "admin"])),
    session: Session = Depends(get_session),
) -> Emprendedor:
    """
    Obtiene el perfil de Emprendedor asociado al usuario autenticado.
    """
    statement = select(Emprendedor).where(Emprendedor.usuario_id == current_user.id)
    emprendedor = session.exec(statement).first()
    if not emprendedor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El usuario no tiene un perfil de emprendedor registrado",
        )
    return emprendedor
