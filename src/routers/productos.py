from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import paginate
from sqlalchemy import func
from sqlmodel import Session, select, col

from src.db.session import get_session
from src.models.emprendedor import Emprendedor
from src.models.producto import Producto, ProductoPublicNested
from src.schemas.producto import ProductoCreate, ProductoRead, ProductoUpdate

from src.models.categoria import Categoria

# Límite de productos uniforme para todos los emprendedores
LIMITE_PRODUCTOS_UNIFORME = 50

router = APIRouter(
    prefix="/productos",
    tags=["Productos"],
)


@router.post(
    "/",
    response_model=ProductoRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo producto",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Emprendedor o Categoría no encontrados",
            "content": {"application/json": {"example": {"detail": "Emprendedor con ID 1 no encontrado"}}},
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Límite máximo de productos alcanzado",
            "content": {"application/json": {"example": {"detail": "Ha alcanzado el límite máximo de 50 productos activos permitidos."}}},
        },
    },
)
def create_producto(
    producto_in: ProductoCreate,
    session: Session = Depends(get_session),
) -> Producto:
    """
    Publica un nuevo producto en el catálogo del emprendedor
    Todos los emprendedores comparten el mismo límite de productos activos
    (LIMITE_PRODUCTOS_UNIFORME = 50).
    """
    # 1. Validar que el emprendedor exista
    emprendedor = session.get(Emprendedor, producto_in.emprendedor_id)
    if not emprendedor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Emprendedor con ID {producto_in.emprendedor_id} no encontrado",
        )

    # 2. Validar que la categoría exista
    categoria = session.get(Categoria, producto_in.categoria_id)
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoría con ID {producto_in.categoria_id} no encontrada",
        )

    # 3. Validar cupo uniforme solo si el producto se crea activo
    if producto_in.activo:
        count_stmt = select(func.count(Producto.id)).where(
            Producto.emprendedor_id == emprendedor.id,
            Producto.activo == True,
        )
        productos_actuales = session.exec(count_stmt).one()
        if productos_actuales >= LIMITE_PRODUCTOS_UNIFORME:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Ha alcanzado el límite máximo de {LIMITE_PRODUCTOS_UNIFORME} productos activos permitidos."
                ),
            )

    # 4. Crear el producto
    producto_db = Producto.model_validate(producto_in)
    session.add(producto_db)
    session.commit()
    session.refresh(producto_db)
    return producto_db


@router.get(
    "/",
    response_model=Page[ProductoRead],
    summary="Listar productos con paginación y filtros de búsqueda",
)
def read_productos(
    categoria_id: Optional[int] = Query(default=None, description="Filtrar por categoría"),
    emprendedor_id: Optional[int] = Query(default=None, description="Filtrar por puesto / emprendedor"),
    en_stock: Optional[bool] = Query(default=None, description="Filtrar por disponibilidad en stock"),
    destacado: Optional[bool] = Query(default=None, description="Filtrar por productos destacados"),
    q: Optional[str] = Query(default=None, description="Buscar por nombre o descripción"),
    activo: Optional[bool] = Query(default=True, description="Filtrar por estado activo"),
    session: Session = Depends(get_session),
):
    """
    Devuelve el catálogo de productos con paginación y soporte de filtros
    """
    statement = select(Producto)

    if categoria_id is not None:
        statement = statement.where(Producto.categoria_id == categoria_id)
    if emprendedor_id is not None:
        statement = statement.where(Producto.emprendedor_id == emprendedor_id)
    if en_stock is not None:
        statement = statement.where(Producto.en_stock == en_stock)
    if destacado is not None:
        statement = statement.where(Producto.destacado == destacado)
    if activo is not None:
        statement = statement.where(Producto.activo == activo)
    if q:
        search_filter = f"%{q.strip()}%"
        statement = statement.where(
            (col(Producto.nombre).ilike(search_filter))
            | (col(Producto.descripcion).ilike(search_filter))
        )

    statement = statement.order_by(Producto.created_at.desc())
    return paginate(session, statement)


@router.get(
    "/{producto_id}",
    response_model=ProductoPublicNested,
    summary="Obtener detalle de un producto",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Producto no encontrado",
            "content": {"application/json": {"example": {"detail": "Producto con ID 1 no encontrado"}}},
        }
    },
)
def read_producto(
    producto_id: int,
    session: Session = Depends(get_session),
) -> Producto:
    """
    Consulta la ficha técnica completa de un producto por su id
    """
    producto = session.get(Producto, producto_id)
    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto con ID {producto_id} no encontrado",
        )
    return producto


@router.put(
    "/{producto_id}",
    response_model=ProductoRead,
    summary="Actualizar un producto",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Producto, categoría o emprendedor no encontrado",
            "content": {"application/json": {"example": {"detail": "Producto con ID 1 no encontrado"}}},
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Límite máximo de productos alcanzado al activar o transferir",
            "content": {"application/json": {"example": {"detail": "Ha alcanzado el límite máximo de 50 productos activos permitidos."}}},
        },
    },
)
def update_producto(
    producto_id: int,
    producto_in: ProductoUpdate,
    session: Session = Depends(get_session),
) -> Producto:
    """
    Actualiza los datos de un producto.
    Valida referencias a categoría y emprendedor si son modificadas, y asegura
    el límite de 50 productos activos si se reactiva o transfiere.
    """
    producto_db = session.get(Producto, producto_id)
    if not producto_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto con ID {producto_id} no encontrado",
        )

    # Validar categoría si se actualiza
    if producto_in.categoria_id is not None:
        categoria = session.get(Categoria, producto_in.categoria_id)
        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Categoría con ID {producto_in.categoria_id} no encontrada",
            )

    # Validar emprendedor si se actualiza
    if producto_in.emprendedor_id is not None:
        nuevo_emprendedor = session.get(Emprendedor, producto_in.emprendedor_id)
        if not nuevo_emprendedor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Emprendedor con ID {producto_in.emprendedor_id} no encontrado",
            )

    # Validar cupo si el producto quedará activo
    nuevo_emprendedor_id = producto_in.emprendedor_id if producto_in.emprendedor_id is not None else producto_db.emprendedor_id
    nuevo_activo = producto_in.activo if producto_in.activo is not None else producto_db.activo

    paso_a_activo = (nuevo_activo is True and producto_db.activo is False)
    cambio_emprendedor_activo = (nuevo_activo is True and nuevo_emprendedor_id != producto_db.emprendedor_id)

    if paso_a_activo or cambio_emprendedor_activo:
        count_stmt = select(func.count(Producto.id)).where(
            Producto.emprendedor_id == nuevo_emprendedor_id,
            Producto.activo == True,
            Producto.id != producto_db.id,
        )
        activos_actuales = session.exec(count_stmt).one()
        if activos_actuales >= LIMITE_PRODUCTOS_UNIFORME:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Ha alcanzado el límite máximo de {LIMITE_PRODUCTOS_UNIFORME} productos activos permitidos.",
            )

    producto_data = producto_in.model_dump(exclude_unset=True)
    for key, value in producto_data.items():
        setattr(producto_db, key, value)

    session.add(producto_db)
    session.commit()
    session.refresh(producto_db)
    return producto_db


@router.delete(
    "/{producto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un producto",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Producto no encontrado",
            "content": {"application/json": {"example": {"detail": "Producto con ID 1 no encontrado"}}},
        }
    },
)
def delete_producto(
    producto_id: int,
    session: Session = Depends(get_session),
) -> None:
    """
    Elimina un producto del catálogo por su id
    """
    producto_db = session.get(Producto, producto_id)
    if not producto_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto con ID {producto_id} no encontrado",
        )

    session.delete(producto_db)
    session.commit()
