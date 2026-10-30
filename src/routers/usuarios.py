from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import paginate
from sqlmodel import Session, select

import bcrypt
from src.db.session import get_session
from src.models.usuario import Usuario, UsuarioCreate, UsuarioPublic, UsuarioUpdate


def hash_password(password: str) -> str:
    """Genera hash seguro para persistir en la columna password_hash."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"],
)


@router.post(
    "/",
    response_model=UsuarioPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo usuario",
)
def create_usuario(
    usuario_in: UsuarioCreate,
    session: Session = Depends(get_session),
) -> Usuario:
    """
    Crea un nuevo usuario en el sistema
    """
    existing_user = session.exec(select(Usuario).where(Usuario.email == usuario_in.email)).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un usuario registrado con este correo electrónico",
        )

    usuario_db = Usuario(
        email=usuario_in.email,
        password_hash=hash_password(usuario_in.password),
        nombre_completo=usuario_in.nombre_completo,
        rol=usuario_in.rol,
        activo=usuario_in.activo,
    )
    session.add(usuario_db)
    session.commit()
    session.refresh(usuario_db)
    return usuario_db


@router.get(
    "/",
    response_model=Page[UsuarioPublic],
    summary="Listar usuarios",
)
def read_usuarios(
    rol: Optional[str] = Query(default=None, description="Filtrar por rol ('cliente', 'emprendedor', 'admin')"),
    activo: Optional[bool] = Query(default=None, description="Filtrar por estado activo"),
    session: Session = Depends(get_session),
):
    """
    Devuelve la lista de usuarios registrados con soportee de paginación.
    """
    statement = select(Usuario)
    if rol is not None:
        statement = statement.where(Usuario.rol == rol)
    if activo is not None:
        statement = statement.where(Usuario.activo == activo)
    return paginate(session, statement)


@router.get(
    "/{usuario_id}",
    response_model=UsuarioPublic,
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
    session: Session = Depends(get_session),
) -> Usuario:
    """
    Consulta los datos de un usuario por su id
    """
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {usuario_id} no encontrado",
        )
    return usuario


@router.put(
    "/{usuario_id}",
    response_model=UsuarioPublic,
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
    session: Session = Depends(get_session),
) -> Usuario:
    """
    Actualiza el perfil de un usuario que ya existe
    """
    usuario_db = session.get(Usuario, usuario_id)
    if not usuario_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {usuario_id} no encontrado",
        )

    data = usuario_in.model_dump(exclude_unset=True)

    # Si se actualiza la contraseña, aplicar hash
    if "password" in data and data["password"]:
        usuario_db.password_hash = hash_password(data.pop("password"))

    for key, value in data.items():
        setattr(usuario_db, key, value)

    session.add(usuario_db)
    session.commit()
    session.refresh(usuario_db)
    return usuario_db


@router.delete(
    "/{usuario_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un usuario",
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
) -> None:
    """
    Elimina un usuario del sistema por su id
    """
    usuario_db = session.get(Usuario, usuario_id)
    if not usuario_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {usuario_id} no encontrado",
        )

    session.delete(usuario_db)
    session.commit()
