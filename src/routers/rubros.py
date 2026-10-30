from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import paginate
from sqlmodel import Session, select

from src.db.session import get_session
from src.models.rubro import Rubro
from src.schemas.rubro import RubroCreate, RubroRead, RubroUpdate

router = APIRouter(
    prefix="/rubros",
    tags=["Rubros"],
)


@router.post(
    "/",
    response_model=RubroRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo rubro",
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
    response_model=RubroRead,
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
    Busca y devuelve un rubro por su id
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
        }
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
        }
    },
)
def delete_rubro(
    rubro_id: int,
    session: Session = Depends(get_session),
) -> None:
    """
    Elimina "físicamente" un rubro de la db
    """
    rubro_db = session.get(Rubro, rubro_id)
    if not rubro_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rubro con ID {rubro_id} no encontrado",
        )

    session.delete(rubro_db)
    session.commit()

