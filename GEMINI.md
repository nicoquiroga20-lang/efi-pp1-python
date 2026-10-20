# GEMINI Context - Feria Imperio (API Backend)

## 📌 Proyecto
- **Nombre:** Feria Imperio - Portal de visibilización y catálogo para feriantes y emprendedores de Río Cuarto.
- **Empresa:** Vertex Solutions S.A.S.
- **Cátedra:** Programación II / Práctica Profesionalizante I - ITEC Río Cuarto.

## 🛠️ Stack Tecnológico Activo
- **Backend:** Python 3.12+, FastAPI, SQLModel (SQLAlchemy + Pydantic), Alembic, Uvicorn, fastapi-pagination, Autenticación de usuarios con JWT.
- **Base de Datos:** SQLite (`database.db`).
- **Frontend / Integración:** React, Vite, TailwindCSS (desarrollado en repo hermano / v1).
- **Carrito de compras:** Simulado en el Frontend (`localStorage`) con despacho coordinado vía enlace a WhatsApp (`wa.me`).

## 📚 Esquema y Modelos de Base de Datos
- **Documento Maestro de Esquema:** @docs/contexto/database_schema.md
  - Define las 8 tablas: `usuarios`, `emprendedores`, `productos`, `planes`, `rubros`, `categorias`, `ferias`, `contactos`.
  - Incluye tipos de datos, llaves foráneas (`FK`), reglas de límites por plan y restricciones de roles.
