from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import paginate
from sqlmodel import Session, select

from src.db.session import get_session
from src.models.emprendedor import (
    Emprendedor,
    EmprendedorCreate,
    EmprendedorPublic,
    EmprendedorPublicNested,
    EmprendedorUpdate,
)
from sqlalchemy import func
from src.models.usuario import Usuario
from src.models.rubro import Rubro
from src.models.feria import Feria
from src.models.producto import Producto

router = APIRouter(
    prefix="/emprendedores",
    tags=["Emprendedores"],
)


@router.post(
    "/",
    response_model=EmprendedorPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo emprendedor / puesto",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Usuario, Rubro o Feria no encontrado",
            "content": {"application/json": {"example": {"detail": "Usuario con ID 1 no encontrado"}}},
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "El usuario ya posee un perfil de emprendedor",
            "content": {"application/json": {"example": {"detail": "El usuario con ID 1 ya posee un perfil de emprendedor"}}},
        },
    },
)
def create_emprendedor(
    emprendedor_in: EmprendedorCreate,
    session: Session = Depends(get_session),
) -> Emprendedor:
    """
    Crea un nuevo perfil de emprendedor de un usuario que ya existe en la db (registrado).
    Valida la existencia del usuario, rubro y feria si es especificada.
    """
    # 1. Validar usuario
    usuario = session.get(Usuario, emprendedor_in.usuario_id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {emprendedor_in.usuario_id} no encontrado",
        )

    # 2. Validar que no tenga ya perfil
    existente = session.exec(
        select(Emprendedor).where(Emprendedor.usuario_id == emprendedor_in.usuario_id)
    ).first()
    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El usuario con ID {emprendedor_in.usuario_id} ya posee un perfil de emprendedor",
        )

    # 3. Validar rubro
    rubro = session.get(Rubro, emprendedor_in.rubro_id)
    if not rubro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rubro con ID {emprendedor_in.rubro_id} no encontrado",
        )

    # 4. Validar feria si se especifica
    if emprendedor_in.feria_id is not None:
        feria = session.get(Feria, emprendedor_in.feria_id)
        if not feria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Feria con ID {emprendedor_in.feria_id} no encontrada",
            )

    emprendedor = Emprendedor.model_validate(emprendedor_in)
    session.add(emprendedor)
    session.commit()
    session.refresh(emprendedor)
    return emprendedor


@router.get(
    "/",
    response_model=Page[EmprendedorPublic],
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
    Devuelve la lista de emprendedores de forma paginada para la vista de puestos en el frontend
    """
    statement = select(Emprendedor) # query a la tabla Emprendedor
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
    Devuelve los datos del puesto/emprendedor por su id (nombre fantasía, bio, whatsApp, banner, etc)
    """
    emprendedor = session.get(Emprendedor, emprendedor_id)
    if not emprendedor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Emprendedor con ID {emprendedor_id} no encontrado",
        )
    return emprendedor


@router.put(
    "/{emprendedor_id}",
    response_model=EmprendedorPublic,
    summary="Actualizar información de un emprendedor",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Emprendedor, Rubro o Feria no encontrado",
            "content": {"application/json": {"example": {"detail": "Emprendedor con ID 1 no encontrado"}}},
        }
    },
)
def update_emprendedor(
    emprendedor_id: int,
    emprendedor_in: EmprendedorUpdate,
    session: Session = Depends(get_session),
) -> Emprendedor:
    """
    Permite actualizar cualquier dato del emprendedor por su id.
    Valida la existencia del nuevo rubro o feria si son modificados.
    """
    emprendedor_db = session.get(Emprendedor, emprendedor_id)
    if not emprendedor_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Emprendedor con ID {emprendedor_id} no encontrado",
        )

    # Validar rubro si se actualiza
    if emprendedor_in.rubro_id is not None:
        rubro = session.get(Rubro, emprendedor_in.rubro_id)
        if not rubro:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rubro con ID {emprendedor_in.rubro_id} no encontrado",
            )

    # Validar feria si se actualiza
    if emprendedor_in.feria_id is not None:
        feria = session.get(Feria, emprendedor_in.feria_id)
        if not feria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Feria con ID {emprendedor_in.feria_id} no encontrada",
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
    summary="Eliminar o dar de baja a un emprendedor",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Emprendedor no encontrado",
            "content": {"application/json": {"example": {"detail": "Emprendedor con ID 1 no encontrado"}}},
        },
        status.HTTP_409_CONFLICT: {
            "description": "Conflicto: posee productos asociados",
            "content": {"application/json": {"example": {"detail": "No se puede eliminar el emprendedor porque posee productos asociados."}}},
        },
    },
)
def delete_emprendedor(
    emprendedor_id: int,
    session: Session = Depends(get_session),
) -> None:
    """
    Elimina un emprendedor de la base de datos por su id.
    Verifica que no tenga productos asociados para prevenir fallos de integridad referencial.
    """
    emprendedor_db = session.get(Emprendedor, emprendedor_id)
    if not emprendedor_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Emprendedor con ID {emprendedor_id} no encontrado",
        )

    # Verificar productos dependientes
    count_prod_stmt = select(func.count(Producto.id)).where(Producto.emprendedor_id == emprendedor_id)
    productos_count = session.exec(count_prod_stmt).one()
    if productos_count > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"No se puede eliminar el emprendedor con ID {emprendedor_id} "
                f"porque posee {productos_count} producto(s) asociado(s). Elimine o reasigne sus productos primero."
            ),
        )

    session.delete(emprendedor_db)
    session.commit()


