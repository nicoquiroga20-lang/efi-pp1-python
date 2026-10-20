from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import paginate
from sqlmodel import Session, select

from src.core.deps import get_current_active_user, get_current_emprendedor, require_roles
from src.db.session import get_session
from src.models.emprendedor import Emprendedor, EmprendedorPublicNested
from src.models.usuario import Usuario
from src.schemas.emprendedor import EmprendedorRead, EmprendedorUpdate

router = APIRouter(
    prefix="/emprendedores",
    tags=["Emprendedores"],
)


@router.get(
    "/",
    response_model=Page[EmprendedorRead],
    summary="Listar emprendedores / puestos con paginación y filtros",
)
def read_emprendedores(
    rubro_id: Optional[int] = Query(default=None, description="Filtrar por rubro"),
    feria_id: Optional[int] = Query(default=None, description="Filtrar por feria habitual"),
    destacado: Optional[bool] = Query(default=None, description="Filtrar por puestos destacados"),
    activo: Optional[bool] = Query(default=True, description="Filtrar por estado activo"),
    session: Session = Depends(get_session),
):
    """
    Retorna la lista de emprendedores de forma paginada para la vista de puestos en el frontend.
    """
    statement = select(Emprendedor)
    if rubro_id is not None:
        statement = statement.where(Emprendedor.rubro_id == rubro_id)
    if feria_id is not None:
        statement = statement.where(Emprendedor.feria_id == feria_id)
    if destacado is not None:
        statement = statement.where(Emprendedor.destacado == destacado)
    if activo is not None:
        statement = statement.where(Emprendedor.activo == activo)

    return paginate(session, statement)


@router.get(
    "/{emprendedor_id}",
    response_model=EmprendedorPublicNested,
    summary="Obtener perfil público de un emprendedor",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Emprendedor no encontrado",
            "content": {"application/json": {"example": {"detail": "Emprendedor con ID 1 no encontrado"}}},
        }
    },
)
def read_emprendedor(
    emprendedor_id: int,
    session: Session = Depends(get_session),
) -> Emprendedor:
    """
    Retorna los datos del puesto/emprendedor por su ID (nombre fantasía, bio, WhatsApp, banner, etc.).
    """
    emprendedor = session.get(Emprendedor, emprendedor_id)
    if not emprendedor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Emprendedor con ID {emprendedor_id} no encontrado",
        )
    return emprendedor


@router.put(
    "/me",
    response_model=EmprendedorRead,
    summary="Actualizar mi propio perfil de emprendedor",
)
def update_my_emprendedor_profile(
    emprendedor_in: EmprendedorUpdate,
    current_emprendedor: Emprendedor = Depends(get_current_emprendedor),
    session: Session = Depends(get_session),
) -> Emprendedor:
    """
    Permite al emprendedor autenticado actualizar la información de su puesto
    (teléfono de WhatsApp, bio, redes sociales, imágenes de banner/logo).
    """
    data = emprendedor_in.model_dump(exclude_unset=True)

    # El emprendedor no puede cambiarse su propio plan ni marcarse como destacado
    data.pop("plan_id", None)
    data.pop("destacado", None)
    data.pop("usuario_id", None)

    for key, value in data.items():
        setattr(current_emprendedor, key, value)

    session.add(current_emprendedor)
    session.commit()
    session.refresh(current_emprendedor)
    return current_emprendedor


@router.put(
    "/{emprendedor_id}",
    response_model=EmprendedorRead,
    summary="Actualizar cualquier emprendedor (Solo Administrador)",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Emprendedor no encontrado",
            "content": {"application/json": {"example": {"detail": "Emprendedor con ID 1 no encontrado"}}},
        }
    },
)
def update_emprendedor_as_admin(
    emprendedor_id: int,
    emprendedor_in: EmprendedorUpdate,
    session: Session = Depends(get_session),
    _admin=Depends(require_roles(["admin"])),
) -> Emprendedor:
    """
    Permite al Administrador gestionar cualquier emprendedor (incluyendo cambiar plan y destacar en Home).
    """
    emprendedor_db = session.get(Emprendedor, emprendedor_id)
    if not emprendedor_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Emprendedor con ID {emprendedor_id} no encontrado",
        )

    data = emprendedor_in.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(emprendedor_db, key, value)

    session.add(emprendedor_db)
    session.commit()
    session.refresh(emprendedor_db)
    return emprendedor_db


@router.delete(
    "/{emprendedor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar o dar de baja a un emprendedor (Solo Administrador)",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Emprendedor no encontrado",
            "content": {"application/json": {"example": {"detail": "Emprendedor con ID 1 no encontrado"}}},
        }
    },
)
def delete_emprendedor(
    emprendedor_id: int,
    session: Session = Depends(get_session),
    _admin=Depends(require_roles(["admin"])),
) -> None:
    """
    Elimina un emprendedor de la base de datos.
    """
    emprendedor_db = session.get(Emprendedor, emprendedor_id)
    if not emprendedor_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Emprendedor con ID {emprendedor_id} no encontrado",
        )

    session.delete(emprendedor_db)
    session.commit()
