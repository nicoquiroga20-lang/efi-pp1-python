from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import paginate
from sqlmodel import Session, select

from src.db.session import get_session
from src.models.categoria import Categoria
from src.schemas.categoria import (
    CategoriaCreate,
    CategoriaRead,
    CategoriaUpdate,
)

router = APIRouter(
    prefix="/categorias",
    tags=["Categorías"],
)


@router.post(
    "/",
    response_model=CategoriaRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva categoría",
)
def create_categoria(
    categoria_in: CategoriaCreate,
    session: Session = Depends(get_session),
) -> Categoria:
    """
    Crea una nueva categoría en la base de datos.
    """
    existing = session.exec(select(Categoria).where(Categoria.nombre == categoria_in.nombre)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe una categoría con el nombre '{categoria_in.nombre}'",
        )

    categoria_db = Categoria.model_validate(categoria_in)
    session.add(categoria_db)
    session.commit()
    session.refresh(categoria_db)
    return categoria_db


@router.get(
    "/",
    response_model=Page[CategoriaRead],
    summary="Listar categorías con paginación",
)
def read_categorias(
    activo: Optional[bool] = Query(default=None, description="Filtrar por estado activo/inactivo"),
    session: Session = Depends(get_session),
):
    """
    Retorna la lista de categorías con soporte para paginación estandarizada y filtrado.
    """
    statement = select(Categoria)
    if activo is not None:
        statement = statement.where(Categoria.activo == activo)
    return paginate(session, statement)


@router.get(
    "/{categoria_id}",
    response_model=CategoriaRead,
    summary="Obtener categoría por ID",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Categoría no encontrada",
            "content": {"application/json": {"example": {"detail": "Categoría con ID 1 no encontrada"}}},
        }
    },
)
def read_categoria(
    categoria_id: int,
    session: Session = Depends(get_session),
) -> Categoria:
    """
    Busca y retorna una categoría específica por su ID.
    """
    categoria = session.get(Categoria, categoria_id)
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoría con ID {categoria_id} no encontrada",
        )
    return categoria


@router.put(
    "/{categoria_id}",
    response_model=CategoriaRead,
    summary="Actualizar una categoría",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Categoría no encontrada",
            "content": {"application/json": {"example": {"detail": "Categoría con ID 1 no encontrada"}}},
        }
    },
)
def update_categoria(
    categoria_id: int,
    categoria_in: CategoriaUpdate,
    session: Session = Depends(get_session),
) -> Categoria:
    """
    Actualiza los campos enviados de una categoría existente.
    """
    categoria_db = session.get(Categoria, categoria_id)
    if not categoria_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoría con ID {categoria_id} no encontrada",
        )

    categoria_data = categoria_in.model_dump(exclude_unset=True)
    for key, value in categoria_data.items():
        setattr(categoria_db, key, value)

    session.add(categoria_db)
    session.commit()
    session.refresh(categoria_db)
    return categoria_db


@router.delete(
    "/{categoria_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una categoría",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Categoría no encontrada",
            "content": {"application/json": {"example": {"detail": "Categoría con ID 1 no encontrada"}}},
        }
    },
)
def delete_categoria(
    categoria_id: int,
    session: Session = Depends(get_session),
) -> None:
    """
    Elimina físicamente una categoría de la base de datos por su ID.
    """
    categoria_db = session.get(Categoria, categoria_id)
    if not categoria_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoría con ID {categoria_id} no encontrada",
        )

    session.delete(categoria_db)
    session.commit()

