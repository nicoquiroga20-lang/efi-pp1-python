"""Alinear la nulabilidad de la clave primaria de emprendedores."""

import sqlalchemy as sa
from alembic import op

revision = "f18d32e705ab"
down_revision = "522b2f09bc01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("emprendedores") as batch:
        batch.alter_column("id", existing_type=sa.Integer(), nullable=False)


def downgrade() -> None:
    with op.batch_alter_table("emprendedores") as batch:
        batch.alter_column("id", existing_type=sa.Integer(), nullable=True)
