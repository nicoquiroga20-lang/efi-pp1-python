from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import paginate
from sqlmodel import Session, select

from src.db.session import get_session
from src.models.plan import Plan
from src.schemas.plan import PlanCreate, PlanRead, PlanUpdate

router = APIRouter(
    prefix="/planes",
    tags=["Planes"],
)


@router.post(
    "/",
    response_model=PlanRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo plan",
)
def create_plan(
    plan_in: PlanCreate,
    session: Session = Depends(get_session),
) -> Plan:
    """
    Crea un nuevo plan de suscripción en el sistema.
    """
    existing = session.exec(select(Plan).where(Plan.nombre == plan_in.nombre)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un plan con el nombre '{plan_in.nombre}'",
        )

    plan_db = Plan.model_validate(plan_in)
    session.add(plan_db)
    session.commit()
    session.refresh(plan_db)
    return plan_db


@router.get(
    "/",
    response_model=Page[PlanRead],
    summary="Listar planes con paginación",
)
def read_planes(
    activo: Optional[bool] = Query(default=None, description="Filtrar por planes activos"),
    session: Session = Depends(get_session),
):
    """
    Retorna la lista de planes disponibles de forma paginada.
    """
    statement = select(Plan)
    if activo is not None:
        statement = statement.where(Plan.activo == activo)
    return paginate(session, statement)


@router.get(
    "/{plan_id}",
    response_model=PlanRead,
    summary="Obtener detalle de un plan",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Plan no encontrado",
            "content": {"application/json": {"example": {"detail": "Plan con ID 1 no encontrado"}}},
        }
    },
)
def read_plan(
    plan_id: int,
    session: Session = Depends(get_session),
) -> Plan:
    """
    Consulta un plan específico por su ID.
    """
    plan = session.get(Plan, plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plan con ID {plan_id} no encontrado",
        )
    return plan


@router.put(
    "/{plan_id}",
    response_model=PlanRead,
    summary="Actualizar un plan",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Plan no encontrado",
            "content": {"application/json": {"example": {"detail": "Plan con ID 1 no encontrado"}}},
        }
    },
)
def update_plan(
    plan_id: int,
    plan_in: PlanUpdate,
    session: Session = Depends(get_session),
) -> Plan:
    """
    Actualiza la información, precio o límites de un plan existente.
    """
    plan_db = session.get(Plan, plan_id)
    if not plan_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plan con ID {plan_id} no encontrado",
        )

    plan_data = plan_in.model_dump(exclude_unset=True)
    for key, value in plan_data.items():
        setattr(plan_db, key, value)

    session.add(plan_db)
    session.commit()
    session.refresh(plan_db)
    return plan_db


@router.delete(
    "/{plan_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Desactivar o eliminar un plan",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Plan no encontrado",
            "content": {"application/json": {"example": {"detail": "Plan con ID 1 no encontrado"}}},
        }
    },
)
def delete_plan(
    plan_id: int,
    session: Session = Depends(get_session),
) -> None:
    """
    Elimina físicamente un plan del sistema.
    """
    plan_db = session.get(Plan, plan_id)
    if not plan_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plan con ID {plan_id} no encontrado",
        )

    session.delete(plan_db)
    session.commit()

