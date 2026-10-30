# Feria Imperio - API Backend

Portal de visibilización y catálogo para feriantes y emprendedores de Río Cuarto.  
**Empresa:** Vertex Solutions S.A.S.  
**Cátedra:** Programación II / Práctica Profesionalizante I - ITEC Río Cuarto.

API REST modular construida con **FastAPI**, **SQLModel** (SQLAlchemy + Pydantic), **SQLite**, migraciones con **Alembic**, paginación estandarizada con **fastapi-pagination** y servidor **Uvicorn**.

---

## 📁 Estructura del Proyecto

```text
efi-pp1-python/
├── .env                  # Variables de entorno activas (ignorado en git)
├── .env.example          # Plantilla de variables de entorno
├── .gitignore            # Reglas de exclusión para Git
├── alembic.ini           # Configuración del motor de migraciones Alembic
├── alembic/              # Control de versiones del esquema de base de datos
│   ├── env.py
│   ├── script.py.mako
│   └── versions/         # Scripts de migración generados
├── database.db           # Base de datos relacional SQLite local
├── docs/                 # Documentación técnica y de contexto del proyecto
│   └── contexto/
│       └── database_schema.md # Documento maestro del esquema de 8 tablas
├── requirements.txt      # Dependencias del proyecto
├── README.md             # Documentación principal del backend
├── tests/                # Suite de pruebas automatizadas
│   ├── test_alembic.py
│   ├── test_crud_and_nested.py
│   ├── test_models_structure.py
│   └── test_openapi_404_docs.py
└── src/
    ├── __init__.py
    ├── main.py           # Instancia principal de FastAPI, CORS, paginación y rutas
    ├── core/             # Configuración central del entorno y aplicación
    │   ├── __init__.py
    │   └── config.py     # Configuración con pydantic-settings
    ├── db/               # Gestión de base de datos
    │   ├── __init__.py
    │   ├── session.py    # Engine de SQLModel y generador get_session
    │   └── init_db.py    # Inicialización de tablas (create_all)
    ├── models/           # Modelos de tabla SQLModel (7 entidades de BD)
    │   ├── __init__.py
    │   ├── usuario.py
    │   ├── emprendedor.py
    │   ├── producto.py
    │   ├── rubro.py
    │   ├── categoria.py
    │   ├── feria.py
    │   └── contacto.py
    ├── schemas/          # Esquemas Pydantic / SQLModel (Create, Read, Update, Nested)
    │   ├── __init__.py
    │   ├── usuario.py
    │   ├── emprendedor.py
    │   ├── producto.py
    │   ├── rubro.py
    │   ├── categoria.py
    │   ├── feria.py
    │   └── contacto.py
    └── routers/          # Path Operations y lógica CRUD pura por entidad
        ├── __init__.py
        ├── usuarios.py
        ├── emprendedores.py
        ├── productos.py
        ├── rubros.py
        ├── categorias.py
        ├── ferias.py
        └── contactos.py
```

---

## 📊 Entidades del Sistema (7 Tablas)

1. **`usuarios`**: Gestión de usuarios (`admin`, `emprendedor`, `cliente`), credenciales y estado activo.
2. **`emprendedores`**: Perfil público del feriante (nombre fantasía, bio, WhatsApp, número de puesto, logos, vinculación a rubro y feria).
3. **`productos`**: Catálogo de productos por emprendedor y categoría (precio, stock, imagen, destacado en Home; límite uniforme de 50 productos).
4. **`rubros`**: Clasificación comercial del puesto (artesanías, gastronomía, indumentaria, etc.).
5. **`categorias`**: Clasificación de artículos individuales para filtrado en el catálogo.
6. **`ferias`**: Cronograma y ubicaciones de ferias presenciales de Río Cuarto.
7. **`contactos`**: Mensajes de contacto y postulaciones de nuevos feriantes.

---

## 🚀 Puesta en Marcha

### 1. Activar el entorno virtual

En Linux / macOS:
```bash
source venv/bin/activate
```

En Windows (PowerShell):
```powershell
venv\Scripts\Activate.ps1
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

Copia el archivo `.env.example` en caso de requerir un nuevo entorno:
```bash
cp .env.example .env
```

Por defecto, la base de datos se aloja en SQLite local:
```env
DATABASE_URL="sqlite:///./database.db"
```

### 4. Migraciones de Base de Datos (Alembic)

Para aplicar las migraciones a la última versión disponible:
```bash
alembic upgrade head
```

### 5. Ejecutar el servidor de desarrollo

```bash
uvicorn src.main:app --reload
```

El servidor quedará activo en [http://localhost:8000](http://localhost:8000).

---

## 📖 Documentación Interactiva de la API

La API cuenta con documentación autogenerada y esquema OpenAPI:

- **Swagger UI**: [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs) (o simplemente `/docs`)
- **ReDoc**: [http://localhost:8000/api/v1/redoc](http://localhost:8000/api/v1/redoc) (o `/redoc`)

---

## 🔌 Resumen de Endpoints CRUD (`/api/v1`)

Todos los recursos cuentan con operaciones CRUD completas, paginación estandarizada (`page` y `size`) y respuestas 404 documentadas:

| Recurso | Endpoints Principales | Descripción |
| :--- | :--- | :--- |
| **Usuarios** | `GET/POST /api/v1/usuarios/`, `GET/PUT/DELETE /api/v1/usuarios/{id}` | CRUD de usuarios y credenciales |
| **Emprendedores** | `GET/POST /api/v1/emprendedores/`, `GET/PUT/DELETE /api/v1/emprendedores/{id}` | Gestión de perfiles de feriantes |
| **Productos** | `GET/POST /api/v1/productos/`, `GET/PUT/DELETE /api/v1/productos/{id}` | Catálogo de productos (límite uniforme de 50 artículos) |
| **Rubros** | `GET/POST /api/v1/rubros/`, `GET/PUT/DELETE /api/v1/rubros/{id}` | Rubros comerciales de feriantes |
| **Categorías** | `GET/POST /api/v1/categorias/`, `GET/PUT/DELETE /api/v1/categorias/{id}` | Categorización de productos |
| **Ferias** | `GET/POST /api/v1/ferias/`, `GET/PUT/DELETE /api/v1/ferias/{id}` | Ubicaciones y fechas de ferias |
| **Contactos** | `GET/POST /api/v1/contactos/`, `GET/PUT/DELETE /api/v1/contactos/{id}` | Bandeja de mensajes y postulaciones |

---

## 🧪 Pruebas Automatizadas

El proyecto incluye 22 pruebas unitarias e integrales que validan la estructura de modelos, migraciones Alembic, contratos OpenAPI (404) y operaciones CRUD:

```bash
python -m unittest discover tests
```
