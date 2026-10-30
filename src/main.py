from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination

from src.core.config import settings
from src.db.init_db import init_db
from src.routers import (
    usuarios_router,
    emprendedores_router,
    productos_router,
    rubros_router,
    categorias_router,
    ferias_router,
    contactos_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Gestión del ciclo de vida de la aplicación.
    Inicializa las 7 tablas en la base de datos relacional al arrancar.
    """
    init_db()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Feria Imperio - API Backend para visibilización y catálogo de feriantes y emprendedores",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan,
)

# Configuración de CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Registro de routers
app.include_router(usuarios_router, prefix=settings.API_V1_STR)
app.include_router(emprendedores_router, prefix=settings.API_V1_STR)
app.include_router(productos_router, prefix=settings.API_V1_STR)
app.include_router(rubros_router, prefix=settings.API_V1_STR)
app.include_router(categorias_router, prefix=settings.API_V1_STR)
app.include_router(ferias_router, prefix=settings.API_V1_STR)
app.include_router(contactos_router, prefix=settings.API_V1_STR)

# Paginación estandarizada global
add_pagination(app)


from fastapi.responses import RedirectResponse


@app.get("/docs", include_in_schema=False)
def redirect_docs():
    return RedirectResponse(url=f"{settings.API_V1_STR}/docs")


@app.get("/redoc", include_in_schema=False)
def redirect_redoc():
    return RedirectResponse(url=f"{settings.API_V1_STR}/redoc")


@app.get("/", tags=["Health Check"])
def root():
    """
    Endpoint raíz para verificar el estado de la API y enlaces a la documentación interactiva.
    """
    return {
        "status": "online",
        "app": settings.PROJECT_NAME,
        "docs": f"{settings.API_V1_STR}/docs",
    }
