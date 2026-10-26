from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import paginate
from sqlmodel import Session, select

from src.db.session import get_session
from src.models.feria import Feria
from src.schemas.feria import FeriaCreate, FeriaRead, FeriaUpdate

router = APIRouter(
    prefix="/ferias",
    tags=["Ferias"],
)


@router.post(
    "/",
    response_model=FeriaRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva feria o evento",
)
def create_feria(
    feria_in: FeriaCreate,
    session: Session = Depends(get_session),
) -> Feria:
    """
    Registra una nueva feria o punto de encuentro en Río Cuarto.
    """
    feria_db = Feria.model_validate(feria_in)
    session.add(feria_db)
    session.commit()
    session.refresh(feria_db)
    return feria_db


@router.get(
    "/",
    response_model=Page[FeriaRead],
    summary="Listar ferias con paginación",
)
def read_ferias(
    activa: Optional[bool] = Query(default=None, description="Filtrar por ferias activas"),
    session: Session = Depends(get_session),
):
    """
    Retorna la lista de ferias y próximas fechas de manera paginada.
    """
    statement = select(Feria)
    if activa is not None:
        statement = statement.where(Feria.activa == activa)
    return paginate(session, statement)


@router.get(
    "/{feria_id}",
    response_model=FeriaRead,
    summary="Obtener detalle de una feria",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Feria no encontrada",
            "content": {"application/json": {"example": {"detail": "Feria con ID 1 no encontrada"}}},
        }
    },
)
def read_feria(
    feria_id: int,
    session: Session = Depends(get_session),
) -> Feria:
    """
    Busca y retorna una feria específica por su ID.
    """
    feria = session.get(Feria, feria_id)
    if not feria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feria con ID {feria_id} no encontrada",
        )
    return feria


@router.put(
    "/{feria_id}",
    response_model=FeriaRead,
    summary="Actualizar una feria",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Feria no encontrada",
            "content": {"application/json": {"example": {"detail": "Feria con ID 1 no encontrada"}}},
        }
    },
)
def update_feria(
    feria_id: int,
    feria_in: FeriaUpdate,
    session: Session = Depends(get_session),
) -> Feria:
    """
    Actualiza la fecha, horario, ubicación o datos de una feria existente.
    """
    feria_db = session.get(Feria, feria_id)
    if not feria_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feria con ID {feria_id} no encontrada",
        )

    feria_data = feria_in.model_dump(exclude_unset=True)
    for key, value in feria_data.items():
        setattr(feria_db, key, value)

    session.add(feria_db)
    session.commit()
    session.refresh(feria_db)
    return feria_db


@router.delete(
    "/{feria_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una feria",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Feria no encontrada",
            "content": {"application/json": {"example": {"detail": "Feria con ID 1 no encontrada"}}},
        }
    },
)
def delete_feria(
    feria_id: int,
    session: Session = Depends(get_session),
) -> None:
    """
    Elimina físicamente una feria de la base de datos.
    """
    feria_db = session.get(Feria, feria_id)
    if not feria_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feria con ID {feria_id} no encontrada",
        )

    session.delete(feria_db)
    session.commit()

