from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import paginate
from sqlalchemy import func
from sqlmodel import Session, select

from src.db.session import get_session
from src.models.categoria import Categoria
from src.models.producto import Producto
from src.schemas.categoria import (
    CategoriaCreate,
    CategoriaRead,
    CategoriaUpdate,
    CategoriaPublicNested,
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
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "Nombre de categoría duplicado",
            "content": {"application/json": {"example": {"detail": "Ya existe una categoría con el nombre 'Indumentaria'"}}},
        }
    },
)
def create_categoria(
    categoria_in: CategoriaCreate,
    session: Session = Depends(get_session),
) -> Categoria:
    """
    Crea una nueva categoría en la db
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
    devuelve la lista de categorías con soporte para paginacióny filtrado.
    """
    statement = select(Categoria)
    if activo is not None:
        statement = statement.where(Categoria.activo == activo)
    return paginate(session, statement)


@router.get(
    "/{categoria_id}",
    response_model=CategoriaPublicNested,
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
    Busca y retorna una categoría por su id junto con sus productos asociados
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
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Nombre de categoría duplicado",
            "content": {"application/json": {"example": {"detail": "Ya existe una categoría con el nombre 'Indumentaria'"}}},
        },
    },
)
def update_categoria(
    categoria_id: int,
    categoria_in: CategoriaUpdate,
    session: Session = Depends(get_session),
) -> Categoria:
    """
    Actualiza los campos enviados de una categoría que ya existe en la db
    """
    categoria_db = session.get(Categoria, categoria_id)
    if not categoria_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoría con ID {categoria_id} no encontrada",
        )

    # Validar unicidad de nombre si fue modificado
    if categoria_in.nombre is not None:
        existente = session.exec(
            select(Categoria).where(
                Categoria.nombre == categoria_in.nombre,
                Categoria.id != categoria_id,
            )
        ).first()
        if existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe una categoría con el nombre '{categoria_in.nombre}'",
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
        },
        status.HTTP_409_CONFLICT: {
            "description": "Conflicto: posee productos asociados",
            "content": {"application/json": {"example": {"detail": "No se puede eliminar la categoría porque posee productos asociados."}}},
        },
    },
)
def delete_categoria(
    categoria_id: int,
    session: Session = Depends(get_session),
) -> None:
    """
    Elimina una categoría de la base de datos por su id.
    Verifica previamente que no existan productos asociados para evitar violaciones de clave foránea.
    """
    categoria_db = session.get(Categoria, categoria_id)
    if not categoria_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoría con ID {categoria_id} no encontrada",
        )

    count_prod_stmt = select(func.count(Producto.id)).where(Producto.categoria_id == categoria_id)
    productos_count = session.exec(count_prod_stmt).one()
    if productos_count > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"No se puede eliminar la categoría con ID {categoria_id} "
                f"porque posee {productos_count} producto(s) asociado(s). Reasigne o elimine los productos primero."
            ),
        )

    session.delete(categoria_db)
    session.commit()

