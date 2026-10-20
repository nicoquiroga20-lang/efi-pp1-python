# EFI - API REST con FastAPI, SQLModel y CRUD

Este proyecto contiene la arquitectura base para una API REST construida con **FastAPI**, **SQLModel** (SQLAlchemy + Pydantic) y **Uvicorn**, diseñada para gestionar operaciones CRUD sobre una base de datos relacional y ser consumida por aplicaciones frontend o clientes externos.

---

## 📁 Estructura del Proyecto

```text
efi-pp1-python/
├── .env                  # Variables de entorno activas (ignorado en git)
├── .env.example          # Plantilla de variables de entorno
├── .gitignore            # Reglas de exclusión para Git
├── requirements.txt      # Dependencias del proyecto
├── README.md             # Documentación del proyecto
└── src/
    ├── __init__.py
    ├── main.py           # Instancia principal de FastAPI, CORS y rutas
    ├── core/
    │   ├── __init__.py
    │   └── config.py     # Configuración con pydantic-settings
    ├── db/
    │   ├── __init__.py
    │   ├── session.py    # Motor de base de datos y dependencia get_session
    │   └── init_db.py    # Inicialización de tablas (create_all)
    ├── models/
    │   ├── __init__.py
    │   └── categoria.py  # Modelo de tabla SQLModel (Base de Datos)
    ├── schemas/
    │   ├── __init__.py
    │   └── categoria.py  # Esquemas Pydantic/SQLModel (Create, Read, Update)
    └── routers/
        ├── __init__.py
        └── categorias.py # Path Operations y operaciones CRUD de categorías
```

---

## 🚀 Puesta en Marcha

### 1. Activar el entorno virtual

Si ya tienes un entorno virtual en la carpeta `venv`:

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

Copia el archivo de ejemplo si no existe `.env`:
```bash
cp .env.example .env
```

Por defecto, la base de datos está configurada con SQLite:
```env
DATABASE_URL="sqlite:///./database.db"
```

> Si deseas usar PostgreSQL o MySQL, simplemente modifica la URL en `.env` (por ejemplo: `postgresql://user:password@localhost:5432/dbname`).

### 4. Ejecutar el servidor

Inicia el servidor en modo desarrollo con recarga automática:

```bash
uvicorn src.main:app --reload
```

El servidor estará disponible en: [http://localhost:8000](http://localhost:8000)

---

## 📖 Documentación Interactiva de la API

Una vez iniciado el servidor, puedes probar y consultar los endpoints directamente en el navegador:

- **Swagger UI**: [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)
- **ReDoc**: [http://localhost:8000/api/v1/redoc](http://localhost:8000/api/v1/redoc)

---

## 🔌 Endpoints CRUD Disponibles (Categorías)

| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| `POST` | `/api/v1/categorias/` | Crear una nueva categoría |
| `GET` | `/api/v1/categorias/` | Listar categorías (con paginación y filtros) |
| `GET` | `/api/v1/categorias/{id}` | Obtener el detalle de una categoría por ID |
| `PUT` | `/api/v1/categorias/{id}` | Actualizar los datos de una categoría |
| `DELETE` | `/api/v1/categorias/{id}` | Eliminar una categoría por ID |
| `GET` | `/` | Health check del servidor |
