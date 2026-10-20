from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import paginate
from sqlalchemy import func
from sqlmodel import Session, select, col

from src.core.deps import get_current_active_user, get_current_emprendedor
from src.db.session import get_session
from src.models.emprendedor import Emprendedor
from src.models.plan import Plan
from src.models.producto import Producto, ProductoPublicNested
from src.models.usuario import Usuario
from src.schemas.producto import ProductoCreate, ProductoRead, ProductoUpdate

router = APIRouter(
    prefix="/productos",
    tags=["Productos"],
)


@router.post(
    "/",
    response_model=ProductoRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo producto (Solo Emprendedores, validando límite de plan)",
)
def create_producto(
    producto_in: ProductoCreate,
    current_emprendedor: Emprendedor = Depends(get_current_emprendedor),
    session: Session = Depends(get_session),
) -> Producto:
    """
    Publica un nuevo producto en el catálogo del emprendedor autenticado.
    
    REGLA DE NEGOCIO:
    Valida que el número de productos activos actuales no supere el 'limite_productos'
    establecido en el Plan asignado al emprendedor.
    """
    # 1. Obtener el plan del emprendedor
    plan = session.get(Plan, current_emprendedor.plan_id)
    limite = plan.limite_productos if plan else 5

    # 2. Contar productos activos del emprendedor
    count_stmt = select(func.count(Producto.id)).where(
        Producto.emprendedor_id == current_emprendedor.id,
        Producto.activo == True,
    )
    productos_actuales = session.exec(count_stmt).one()

    # 3. Validar cupo
    if productos_actuales >= limite:
        nombre_plan = plan.nombre if plan else "Plan actual"
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                f"Ha alcanzado el límite máximo de productos de su plan '{nombre_plan}' "
                f"({limite} productos permitidos). Actualice su plan para publicar más artículos."
            ),
        )

    # 4. Crear el producto asignado al emprendedor en sesión
    producto_data = producto_in.model_dump()
    producto_db = Producto(
        **producto_data,
        emprendedor_id=current_emprendedor.id,
    )
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
    Retorna el catálogo de productos con paginación y soporte de filtros múltiples.
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
    Consulta la ficha técnica completa de un producto por su ID.
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
    summary="Actualizar un producto (Emprendedor dueño o Administrador)",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Producto no encontrado",
            "content": {"application/json": {"example": {"detail": "Producto con ID 1 no encontrado"}}},
        }
    },
)
def update_producto(
    producto_id: int,
    producto_in: ProductoUpdate,
    current_user: Usuario = Depends(get_current_active_user),
    session: Session = Depends(get_session),
) -> Producto:
    """
    Actualiza los datos de un producto.
    El emprendedor solo puede modificar sus propios productos; el Admin puede modificar cualquiera.
    """
    producto_db = session.get(Producto, producto_id)
    if not producto_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto con ID {producto_id} no encontrado",
        )

    # Validar permisos de edición
    if current_user.rol != "admin":
        emprendedor_stmt = select(Emprendedor).where(Emprendedor.usuario_id == current_user.id)
        current_emp = session.exec(emprendedor_stmt).first()
        if not current_emp or producto_db.emprendedor_id != current_emp.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permiso para modificar este producto",
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
    summary="Eliminar un producto (Emprendedor dueño o Administrador)",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Producto no encontrado",
            "content": {"application/json": {"example": {"detail": "Producto con ID 1 no encontrado"}}},
        }
    },
)
def delete_producto(
    producto_id: int,
    current_user: Usuario = Depends(get_current_active_user),
    session: Session = Depends(get_session),
) -> None:
    """
    Elimina un producto del catálogo.
    El emprendedor solo puede eliminar sus propios productos; el Admin puede eliminar cualquiera.
    """
    producto_db = session.get(Producto, producto_id)
    if not producto_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto con ID {producto_id} no encontrado",
        )

    # Validar permisos
    if current_user.rol != "admin":
        emprendedor_stmt = select(Emprendedor).where(Emprendedor.usuario_id == current_user.id)
        current_emp = session.exec(emprendedor_stmt).first()
        if not current_emp or producto_db.emprendedor_id != current_emp.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permiso para eliminar este producto",
            )

    session.delete(producto_db)
    session.commit()
