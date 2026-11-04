# Feria Imperio - API Backend

Portal de visibilización y catálogo para feriantes y emprendedores de Río Cuarto.  
**Empresa:** Vertex Solutions S.A.S.  
**Cátedra:** Programación II / Práctica Profesionalizante I - ITEC Río Cuarto.

API REST modular construida con **FastAPI**, **SQLModel** (SQLAlchemy + Pydantic), **SQLite**, migraciones con **Alembic**, paginación estandarizada con **fastapi-pagination** y servidor **Uvicorn**.

## 👥 Integrantes del Equipo
- **Alejo Alaminos**
- **Joaquin Fornasari**
- **Franco Leone**
- **Mauricio Nicolas Quiroga**

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
│   ├── README            # Documentación del entorno de migraciones
│   ├── script.py.mako
│   └── versions/         # Scripts de migración generados
├── database.db           # Base de datos relacional SQLite local
├── docs/                 # Documentación técnica y de contexto del proyecto
│   └── contexto/
│       └── database_schema.md # Documento maestro del esquema de tablas
├── pyproject.toml        # Configuración de empaquetado y despliegue (FastAPI Cloud)
├── requirements.txt      # Dependencias del proyecto
├── README.md             # Documentación principal del backend
├── tests/                # Suite de pruebas automatizadas
│   ├── __init__.py
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
    │   └── init_db.py    # Aplicación de migraciones al arrancar
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

----

## 🔌 Resumen de Endpoints CRUD (`/api/v1`)

Todos los recursos cuentan con operaciones CRUD completas, paginación estandarizada (`page` y `size`), esquemas anidados (`Nested`) para entidades con relaciones y respuestas `404`, `400` y `409` (Conflict por integridad referencial) documentadas en OpenAPI:

| Recurso | Endpoints Principales | Esquema Anidado (GET /{id}) | Descripción |
| :--- | :--- | :--- | :--- |
| **Usuarios** | `GET/POST /api/v1/usuarios/`, `GET/PUT/DELETE /api/v1/usuarios/{id}` | `UsuarioPublicNested` (+ emprendedor) | CRUD de usuarios, credenciales hasheadas y prevención de borrado con emprendedor vinculado (`409`) |
| **Emprendedores** | `GET/POST /api/v1/emprendedores/`, `GET/PUT/DELETE /api/v1/emprendedores/{id}` | `EmprendedorPublicNested` (+ rubro, feria, usuario, productos) | Gestión de feriantes, validación de foráneas (`404`) y prevención de borrado con productos (`409`) |
| **Productos** | `GET/POST /api/v1/productos/`, `GET/PUT/DELETE /api/v1/productos/{id}` | `ProductoPublicNested` (+ categoría, emprendedor) | Catálogo con límite uniforme de 50 artículos activos (controlado en creación y reactivación) |
| **Rubros** | `GET/POST /api/v1/rubros/`, `GET/PUT/DELETE /api/v1/rubros/{id}` | `RubroPublicNested` (+ emprendedores) | Rubros comerciales, nombres únicos y prevención de borrado con emprendedores (`409`) |
| **Categorías** | `GET/POST /api/v1/categorias/`, `GET/PUT/DELETE /api/v1/categorias/{id}` | `CategoriaPublicNested` (+ productos) | Categorización de productos, nombres únicos y prevención de borrado con productos (`409`) |
| **Ferias** | `GET/POST /api/v1/ferias/`, `GET/PUT/DELETE /api/v1/ferias/{id}` | `FeriaPublicNested` (+ emprendedores) | Cronograma de ferias y prevención de borrado con emprendedores asignados (`409`) |
| **Contactos** | `GET/POST /api/v1/contactos/`, `GET/PUT/DELETE /api/v1/contactos/{id}` | `ContactoPublic` | Bandeja de mensajes y postulaciones con filtrado |

---

