from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import paginate
from sqlmodel import Session, select

from src.core.deps import require_roles
from src.db.session import get_session
from src.models.contacto import Contacto
from src.schemas.contacto import ContactoCreate, ContactoRead, ContactoUpdate

router = APIRouter(
    prefix="/contactos",
    tags=["Contactos"],
)


@router.post(
    "/",
    response_model=ContactoRead,
    status_code=status.HTTP_201_CREATED,
    summary="Enviar mensaje de contacto o postulación (Público)",
)
def create_contacto(
    contacto_in: ContactoCreate,
    session: Session = Depends(get_session),
) -> Contacto:
    """
    Envía una consulta o postulación desde el formulario de contacto web.
    Cualquier visitante puede enviar un mensaje sin registrarse.
    """
    contacto_db = Contacto.model_validate(contacto_in)
    session.add(contacto_db)
    session.commit()
    session.refresh(contacto_db)
    return contacto_db


@router.get(
    "/",
    response_model=Page[ContactoRead],
    summary="Listar mensajes de contacto (Solo Administrador)",
)
def read_contactos(
    leido: Optional[bool] = Query(default=None, description="Filtrar por estado leído/no leído"),
    tipo_mensaje: Optional[str] = Query(default=None, description="Filtrar por tipo de mensaje"),
    session: Session = Depends(get_session),
    _admin=Depends(require_roles(["admin"])),
):
    """
    Permite al Administrador revisar la bandeja de entrada de mensajes de contacto y postulaciones.
    """
    statement = select(Contacto)
    if leido is not None:
        statement = statement.where(Contacto.leido == leido)
    if tipo_mensaje is not None:
        statement = statement.where(Contacto.tipo_mensaje == tipo_mensaje)
    statement = statement.order_by(Contacto.created_at.desc())
    return paginate(session, statement)


@router.get(
    "/{contacto_id}",
    response_model=ContactoRead,
    summary="Ver detalle de un mensaje de contacto (Solo Administrador)",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Mensaje de contacto no encontrado",
            "content": {"application/json": {"example": {"detail": "Mensaje de contacto con ID 1 no encontrado"}}},
        }
    },
)
def read_contacto(
    contacto_id: int,
    session: Session = Depends(get_session),
    _admin=Depends(require_roles(["admin"])),
) -> Contacto:
    """
    Lee un mensaje de contacto específico y puede marcarlo automáticamente como leído.
    """
    contacto = session.get(Contacto, contacto_id)
    if not contacto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mensaje de contacto con ID {contacto_id} no encontrado",
        )
    return contacto


@router.put(
    "/{contacto_id}",
    response_model=ContactoRead,
    summary="Actualizar estado de un mensaje (Solo Administrador)",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Mensaje de contacto no encontrado",
            "content": {"application/json": {"example": {"detail": "Mensaje de contacto con ID 1 no encontrado"}}},
        }
    },
)
def update_contacto(
    contacto_id: int,
    contacto_in: ContactoUpdate,
    session: Session = Depends(get_session),
    _admin=Depends(require_roles(["admin"])),
) -> Contacto:
    """
    Permite marcar un mensaje como leído o pendiente.
    """
    contacto_db = session.get(Contacto, contacto_id)
    if not contacto_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mensaje de contacto con ID {contacto_id} no encontrado",
        )

    contacto_data = contacto_in.model_dump(exclude_unset=True)
    for key, value in contacto_data.items():
        setattr(contacto_db, key, value)

    session.add(contacto_db)
    session.commit()
    session.refresh(contacto_db)
    return contacto_db


@router.delete(
    "/{contacto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un mensaje de contacto (Solo Administrador)",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Mensaje de contacto no encontrado",
            "content": {"application/json": {"example": {"detail": "Mensaje de contacto con ID 1 no encontrado"}}},
        }
    },
)
def delete_contacto(
    contacto_id: int,
    session: Session = Depends(get_session),
    _admin=Depends(require_roles(["admin"])),
) -> None:
    """
    Elimina un mensaje de contacto de la bandeja de entrada.
    """
    contacto_db = session.get(Contacto, contacto_id)
    if not contacto_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mensaje de contacto con ID {contacto_id} no encontrado",
        )

    session.delete(contacto_db)
    session.commit()
