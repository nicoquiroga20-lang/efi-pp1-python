# Esquema de Base de Datos - Feria Imperio (FastAPI + SQLModel + SQLite)

> **Contexto del Proyecto:**  
> Este documento define la estructura oficial de las 7 tablas de la base de datos relacional (SQLite) para la API de **Feria Imperio**, desarrollada por Vertex Solutions S.A.S. para la Tecnicatura Superior en Desarrollo de Software (ITEC).  
> **Alcance de Pedidos/Carrito:** El carrito de compras se gestiona en el Frontend (`localStorage`) y la compra se finaliza mediante coordinación directa por WhatsApp. Por lo tanto, no se requiere tabla transaccional de órdenes/pedidos en la versión 1.

---

## 📊 Resumen de las 7 Tablas

| # | Tabla (`__tablename__`) | Modelo SQLModel | Descripción / Propósito |
|---|-------------------------|-----------------|-------------------------|
| 1 | `usuarios`              | `Usuario`       | Gestión de usuarios y control de roles (`admin`, `emprendedor`, `cliente`). |
| 2 | `emprendedores`         | `Emprendedor`   | Perfil público del puesto/feriante, bio, WhatsApp, rubro y feria asignada. |
| 3 | `productos`             | `Producto`      | Catálogo de productos publicados por cada emprendedor (límite uniforme). |
| 4 | `rubros`                | `Rubro`         | Clasificación del emprendimiento (ej: Artesanías, Gastronomía, Cuero). |
| 5 | `categorias`            | `Categoria`     | Clasificación específica de productos (ej: Mates, Billeteras, Mermeladas). |
| 6 | `ferias`                | `Feria`         | Fechas y ubicaciones de ferias locales (ej: Parque Sarmiento, Paseo del Andino). |
| 7 | `contactos`             | `Contacto`      | Mensajes del formulario de contacto y solicitudes de nuevos feriantes. |

---

## 🛠️ Detalle de Tablas y Campos

### 1. `usuarios` (`Usuario`)
Gestiona el acceso, credenciales y permisos en la API.
```python
class Usuario(SQLModel, table=True):
    __tablename__ = "usuarios"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=150, nullable=False)
    password_hash: str = Field(nullable=False)
    nombre_completo: str = Field(max_length=150, nullable=False)
    rol: str = Field(default="cliente", max_length=20)  # 'cliente', 'emprendedor', 'admin'
    activo: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

### 2. `emprendedores` (`Emprendedor`)
Perfil comercial de los feriantes. Vinculado 1:1 con un usuario de rol `'emprendedor'`.
```python
class Emprendedor(SQLModel, table=True):
    __tablename__ = "emprendedores"

    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuarios.id", unique=True, nullable=False)
    nombre_fantasia: str = Field(index=True, max_length=150, nullable=False)
    descripcion_bio: Optional[str] = Field(default=None, max_length=500)
    telefono_whatsapp: str = Field(max_length=30, nullable=False)  # Base para checkout por WhatsApp
    instagram: Optional[str] = Field(default=None, max_length=100)
    numero_puesto: Optional[str] = Field(default=None, max_length=50)
    logo_url: Optional[str] = Field(default=None, max_length=255)
    banner_url: Optional[str] = Field(default=None, max_length=255)
    rubro_id: int = Field(foreign_key="rubros.id", nullable=False)
    feria_id: Optional[int] = Field(default=None, foreign_key="ferias.id")
    destacado: bool = Field(default=False)
    activo: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

### 3. `productos` (`Producto`)
Artículos que vende cada emprendedor en su catálogo.
```python
class Producto(SQLModel, table=True):
    __tablename__ = "productos"

    id: Optional[int] = Field(default=None, primary_key=True)
    emprendedor_id: int = Field(foreign_key="emprendedores.id", nullable=False)
    categoria_id: int = Field(foreign_key="categorias.id", nullable=False)
    nombre: str = Field(index=True, max_length=150, nullable=False)
    descripcion: Optional[str] = Field(default=None, max_length=500)
    precio: float = Field(nullable=False)
    imagen_url: Optional[str] = Field(default=None, max_length=255)
    en_stock: bool = Field(default=True)
    destacado: bool = Field(default=False)  # Destacado en Home
    activo: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

### 4. `rubros` (`Rubro`)
Clasificación comercial del emprendimiento (rubro del puesto).
```python
class Rubro(SQLModel, table=True):
    __tablename__ = "rubros"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(unique=True, index=True, max_length=100, nullable=False)
    descripcion: Optional[str] = Field(default=None, max_length=255)
    activo: bool = Field(default=True)
```

### 5. `categorias` (`Categoria`)
Categorización de artículos individuales (en `src/models/categoria.py`).
```python
class Categoria(SQLModel, table=True):
    __tablename__ = "categorias"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(unique=True, index=True, max_length=100, nullable=False)
    descripcion: Optional[str] = Field(default=None, max_length=255)
    activo: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

### 6. `ferias` (`Feria`)
Lugares y cronograma de las ferias presenciales de Río Cuarto.
```python
class Feria(SQLModel, table=True):
    __tablename__ = "ferias"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=150, nullable=False)  # Ej: 'Paseo del Andino', 'Parque Sarmiento'
    ubicacion: str = Field(max_length=255, nullable=False)
    proxima_fecha: Optional[datetime] = Field(default=None)
    horario: Optional[str] = Field(default=None, max_length=100)  # Ej: '15:00 a 20:00 hs'
    descripcion: Optional[str] = Field(default=None, max_length=500)
    activa: bool = Field(default=True)
```

### 7. `contactos` (`Contacto`)
Bandeja de entrada para consultas de visitantes y postulaciones de feriantes.
```python
class Contacto(SQLModel, table=True):
    __tablename__ = "contactos"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre_completo: str = Field(max_length=150, nullable=False)
    email: str = Field(max_length=150, nullable=False)
    telefono: Optional[str] = Field(default=None, max_length=50)
    tipo_mensaje: str = Field(default="consulta_general", max_length=50)  # 'consulta_general', 'postulacion_puesto', 'feedback'
    mensaje: str = Field(nullable=False)
    leido: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

---

## ⚙️ Reglas de Negocio en Backend

1. **Validación del Límite Uniforme al crear Producto:**
   - Endpoint: `POST /api/v1/productos/`
   - Lógica: Todos los feriantes gozan de los mismos beneficios. El cupo máximo compartido es de 50 productos activos (`LIMITE_PRODUCTOS_UNIFORME = 50`). Si `conteo >= 50`, la API responde `HTTP 403 Forbidden` impidiendo la creación del producto.
2. **Relación Emprendedor - Usuario:**
   - Cada perfil de emprendedor se vincula 1:1 con un usuario (`usuario_id` único).
3. **Acceso a Entidades:**
   - Acceso a operaciones CRUD de `rubros`, `categorias`, `ferias`, gestión de feriantes y lectura de mensajes en `contactos`.
