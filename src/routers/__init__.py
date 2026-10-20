from src.routers.auth import router as auth_router
from src.routers.usuarios import router as usuarios_router
from src.routers.planes import router as planes_router
from src.routers.rubros import router as rubros_router
from src.routers.categorias import router as categorias_router
from src.routers.ferias import router as ferias_router
from src.routers.contactos import router as contactos_router
from src.routers.emprendedores import router as emprendedores_router
from src.routers.productos import router as productos_router

__all__ = [
    "auth_router",
    "usuarios_router",
    "planes_router",
    "rubros_router",
    "categorias_router",
    "ferias_router",
    "contactos_router",
    "emprendedores_router",
    "productos_router",
]
