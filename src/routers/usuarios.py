from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import paginate
from sqlmodel import Session, select

from src.core.deps import get_current_active_user, require_roles
from src.core.security import get_password_hash
from src.db.session import get_session
from src.models.usuario import Usuario
from src.schemas.usuario import UsuarioRead, UsuarioUpdate

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"],
)


@router.get(
    "/",
    response_model=Page[UsuarioRead],
    summary="Listar usuarios (Solo Administrador)",
)
def read_usuarios(
    rol: Optional[str] = Query(default=None, description="Filtrar por rol ('cliente', 'emprendedor', 'admin')"),
    activo: Optional[bool] = Query(default=None, description="Filtrar por estado activo"),
    session: Session = Depends(get_session),
    _admin=Depends(require_roles(["admin"])),
):
    """
    Retorna la lista de usuarios registrados con soporte de paginación.
    """
    statement = select(Usuario)
    if rol is not None:
        statement = statement.where(Usuario.rol == rol)
    if activo is not None:
        statement = statement.where(Usuario.activo == activo)
    return paginate(session, statement)


@router.get(
    "/{usuario_id}",
    response_model=UsuarioRead,
    summary="Obtener usuario por ID",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Usuario no encontrado",
            "content": {"application/json": {"example": {"detail": "Usuario con ID 1 no encontrado"}}},
        }
    },
)
def read_usuario(
    usuario_id: int,
    current_user: Usuario = Depends(get_current_active_user),
    session: Session = Depends(get_session),
) -> Usuario:
    """
    Consulta los datos de un usuario por su ID.
    Solo el Administrador o el propio usuario pueden consultar su información.
    """
    if current_user.rol != "admin" and current_user.id != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permiso para ver la información de este usuario",
        )

    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {usuario_id} no encontrado",
        )
    return usuario


@router.put(
    "/{usuario_id}",
    response_model=UsuarioRead,
    summary="Actualizar datos de un usuario",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Usuario no encontrado",
            "content": {"application/json": {"example": {"detail": "Usuario con ID 1 no encontrado"}}},
        }
    },
)
def update_usuario(
    usuario_id: int,
    usuario_in: UsuarioUpdate,
    current_user: Usuario = Depends(get_current_active_user),
    session: Session = Depends(get_session),
) -> Usuario:
    """
    Actualiza el perfil de un usuario.
    Los usuarios comunes pueden editar su nombre o password; solo Admin puede cambiar rol o estado activo.
    """
    if current_user.rol != "admin" and current_user.id != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permiso para modificar este usuario",
        )

    usuario_db = session.get(Usuario, usuario_id)
    if not usuario_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {usuario_id} no encontrado",
        )

    data = usuario_in.model_dump(exclude_unset=True)

    # Si no es admin, no puede cambiar rol ni estado activo
    if current_user.rol != "admin":
        data.pop("rol", None)
        data.pop("activo", None)

    # Si se actualiza la contraseña, aplicar hash
    if "password" in data and data["password"]:
        usuario_db.password_hash = get_password_hash(data.pop("password"))

    for key, value in data.items():
        setattr(usuario_db, key, value)

    session.add(usuario_db)
    session.commit()
    session.refresh(usuario_db)
    return usuario_db


@router.delete(
    "/{usuario_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Desactivar o eliminar un usuario (Solo Administrador)",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Usuario no encontrado",
            "content": {"application/json": {"example": {"detail": "Usuario con ID 1 no encontrado"}}},
        }
    },
)
def delete_usuario(
    usuario_id: int,
    session: Session = Depends(get_session),
    _admin=Depends(require_roles(["admin"])),
) -> None:
    """
    Desactiva o elimina un usuario del sistema.
    """
    usuario_db = session.get(Usuario, usuario_id)
    if not usuario_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {usuario_id} no encontrado",
        )

    session.delete(usuario_db)
    session.commit()
