from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import paginate
from sqlalchemy import func
from sqlmodel import Session, select

from src.db.session import get_session
from src.models.rubro import Rubro
from src.models.emprendedor import Emprendedor
from src.schemas.rubro import (
    RubroCreate,
    RubroRead,
    RubroUpdate,
    RubroPublicNested,
)

router = APIRouter(
    prefix="/rubros",
    tags=["Rubros"],
)


@router.post(
    "/",
    response_model=RubroRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo rubro",
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "Nombre de rubro duplicado",
            "content": {"application/json": {"example": {"detail": "Ya existe un rubro con el nombre 'Gastronomía'"}}},
        }
    },
)
def create_rubro(
    rubro_in: RubroCreate,
    session: Session = Depends(get_session),
) -> Rubro:
    """
    Crea un nuevo rubro para clasificar emprendimientos
    """
    existing = session.exec(select(Rubro).where(Rubro.nombre == rubro_in.nombre)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un rubro con el nombre '{rubro_in.nombre}'",
        )

    rubro_db = Rubro.model_validate(rubro_in)
    session.add(rubro_db)
    session.commit()
    session.refresh(rubro_db)
    return rubro_db


@router.get(
    "/",
    response_model=Page[RubroRead],
    summary="Listar rubros con paginación",
)
def read_rubros(
    activo: Optional[bool] = Query(default=None, description="Filtrar por rubros activos"),
    session: Session = Depends(get_session),
):
    """
    Devuelve la lista de rubros de manera paginada
    """
    statement = select(Rubro)
    if activo is not None:
        statement = statement.where(Rubro.activo == activo)
    return paginate(session, statement)


@router.get(
    "/{rubro_id}",
    response_model=RubroPublicNested,
    summary="Obtener detalle de un rubro",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Rubro no encontrado",
            "content": {"application/json": {"example": {"detail": "Rubro con ID 1 no encontrado"}}},
        }
    },
)
def read_rubro(
    rubro_id: int,
    session: Session = Depends(get_session),
) -> Rubro:
    """
    Busca y devuelve un rubro por su id con sus emprendedores asociados
    """
    rubro = session.get(Rubro, rubro_id)
    if not rubro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rubro con ID {rubro_id} no encontrado",
        )
    return rubro


@router.put(
    "/{rubro_id}",
    response_model=RubroRead,
    summary="Actualizar un rubro",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Rubro no encontrado",
            "content": {"application/json": {"example": {"detail": "Rubro con ID 1 no encontrado"}}},
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Nombre de rubro duplicado",
            "content": {"application/json": {"example": {"detail": "Ya existe un rubro con el nombre 'Gastronomía'"}}},
        },
    },
)
def update_rubro(
    rubro_id: int,
    rubro_in: RubroUpdate,
    session: Session = Depends(get_session),
) -> Rubro:
    """
    Actualiza el nombre o descripción de un rubro existente
    """
    rubro_db = session.get(Rubro, rubro_id)
    if not rubro_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rubro con ID {rubro_id} no encontrado",
        )

    if rubro_in.nombre is not None:
        existente = session.exec(
            select(Rubro).where(
                Rubro.nombre == rubro_in.nombre,
                Rubro.id != rubro_id,
            )
        ).first()
        if existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un rubro con el nombre '{rubro_in.nombre}'",
            )

    rubro_data = rubro_in.model_dump(exclude_unset=True)
    for key, value in rubro_data.items():
        setattr(rubro_db, key, value)

    session.add(rubro_db)
    session.commit()
    session.refresh(rubro_db)
    return rubro_db


@router.delete(
    "/{rubro_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un rubro",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Rubro no encontrado",
            "content": {"application/json": {"example": {"detail": "Rubro con ID 1 no encontrado"}}},
        },
        status.HTTP_409_CONFLICT: {
            "description": "Conflicto: posee emprendedores asociados",
            "content": {"application/json": {"example": {"detail": "No se puede eliminar el rubro porque posee emprendedores asociados."}}},
        },
    },
)
def delete_rubro(
    rubro_id: int,
    session: Session = Depends(get_session),
) -> None:
    """
    Elimina un rubro de la base de datos por su id.
    Verifica que no tenga emprendedores asociados antes de proceder.
    """
    rubro_db = session.get(Rubro, rubro_id)
    if not rubro_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rubro con ID {rubro_id} no encontrado",
        )

    count_emp_stmt = select(func.count(Emprendedor.id)).where(Emprendedor.rubro_id == rubro_id)
    emprendedores_count = session.exec(count_emp_stmt).one()
    if emprendedores_count > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"No se puede eliminar el rubro con ID {rubro_id} "
                f"porque posee {emprendedores_count} emprendedor(es) asociado(s). Reasigne o elimine los emprendedores primero."
            ),
        )

    session.delete(rubro_db)
    session.commit()


