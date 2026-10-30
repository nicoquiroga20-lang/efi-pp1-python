"""eliminar_tabla_planes_y_columna_plan_id_en_emprendedores

Revision ID: 522b2f09bc01
Revises: a0a3dd99a5e2
Create Date: 2026-10-29 11:21:44.659668

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '522b2f09bc01'
down_revision: Union[str, Sequence[str], None] = 'a0a3dd99a5e2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # SQLite no soporta DROP COLUMN directamente.
    # batch_alter_table reconstruye la tabla, pero falla al reflejar
    # la FK a 'planes' si ésta ya no existe. Solución: ejecutar el DROP COLUMN
    # con SQL puro vía recreación manual, o usar execute() directamente.
    # Dado que SQLite no tiene DROP COLUMN hasta la v3.35, usamos el enfoque
    # de reconstrucción directa con raw SQL para evitar la reflexión de FK.

    bind = op.get_bind()

    # 1. Recrear emprendedores sin la columna plan_id (sin FK a planes)
    bind.execute(sa.text("""
        CREATE TABLE emprendedores_new (
            nombre_fantasia VARCHAR(150) NOT NULL,
            descripcion_bio VARCHAR(500),
            telefono_whatsapp VARCHAR(30) NOT NULL,
            instagram VARCHAR(100),
            numero_puesto VARCHAR(50),
            logo_url VARCHAR(255),
            banner_url VARCHAR(255),
            rubro_id INTEGER NOT NULL REFERENCES rubros(id),
            feria_id INTEGER REFERENCES ferias(id),
            destacado BOOLEAN NOT NULL,
            activo BOOLEAN NOT NULL,
            id INTEGER PRIMARY KEY,
            usuario_id INTEGER NOT NULL UNIQUE REFERENCES usuarios(id),
            created_at DATETIME NOT NULL
        )
    """))

    bind.execute(sa.text("""
        INSERT INTO emprendedores_new
        SELECT
            nombre_fantasia, descripcion_bio, telefono_whatsapp, instagram,
            numero_puesto, logo_url, banner_url, rubro_id, feria_id,
            destacado, activo, id, usuario_id, created_at
        FROM emprendedores
    """))

    bind.execute(sa.text("DROP TABLE emprendedores"))
    bind.execute(sa.text("ALTER TABLE emprendedores_new RENAME TO emprendedores"))

    # Recrear índice
    bind.execute(sa.text(
        "CREATE INDEX ix_emprendedores_nombre_fantasia ON emprendedores (nombre_fantasia)"
    ))

    # 2. Eliminar la tabla planes
    bind.execute(sa.text("DROP INDEX IF EXISTS ix_planes_nombre"))
    bind.execute(sa.text("DROP TABLE IF EXISTS planes"))


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()

    # Recrear tabla planes
    bind.execute(sa.text("""
        CREATE TABLE planes (
            id INTEGER PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            limite_productos INTEGER NOT NULL,
            precio_mensual FLOAT NOT NULL,
            permite_destacados BOOLEAN NOT NULL,
            descripcion VARCHAR(255),
            activo BOOLEAN NOT NULL,
            created_at DATETIME NOT NULL
        )
    """))
    bind.execute(sa.text("CREATE UNIQUE INDEX ix_planes_nombre ON planes (nombre)"))

    # Insertar plan base id=1 para que los emprendedores tengan una referencia válida
    bind.execute(sa.text("""
        INSERT INTO planes (id, nombre, limite_productos, precio_mensual, permite_destacados, descripcion, activo, created_at)
        VALUES (1, 'Plan Base Inicial', 50, 0.0, 1, 'Plan base asignado por downgrade', 1, CURRENT_TIMESTAMP)
    """))

    # Recrear emprendedores con plan_id
    bind.execute(sa.text("""
        CREATE TABLE emprendedores_old (
            nombre_fantasia VARCHAR(150) NOT NULL,
            descripcion_bio VARCHAR(500),
            telefono_whatsapp VARCHAR(30) NOT NULL,
            instagram VARCHAR(100),
            numero_puesto VARCHAR(50),
            logo_url VARCHAR(255),
            banner_url VARCHAR(255),
            rubro_id INTEGER NOT NULL REFERENCES rubros(id),
            feria_id INTEGER REFERENCES ferias(id),
            plan_id INTEGER NOT NULL DEFAULT 1 REFERENCES planes(id),
            destacado BOOLEAN NOT NULL,
            activo BOOLEAN NOT NULL,
            id INTEGER PRIMARY KEY,
            usuario_id INTEGER NOT NULL UNIQUE REFERENCES usuarios(id),
            created_at DATETIME NOT NULL
        )
    """))
    bind.execute(sa.text("""
        INSERT INTO emprendedores_old
        SELECT
            nombre_fantasia, descripcion_bio, telefono_whatsapp, instagram,
            numero_puesto, logo_url, banner_url, rubro_id, feria_id,
            1, destacado, activo, id, usuario_id, created_at
        FROM emprendedores
    """))
    bind.execute(sa.text("DROP TABLE emprendedores"))
    bind.execute(sa.text("ALTER TABLE emprendedores_old RENAME TO emprendedores"))
    bind.execute(sa.text(
        "CREATE INDEX ix_emprendedores_nombre_fantasia ON emprendedores (nombre_fantasia)"
    ))
