# pylint: skip-file
"""
Se saco la columna admins, pues se movio toda la logica de log in a otro servicio, y ahora para saber si es admin o no, se le pregunta al gateway.

Revision ID: b46bff422020
Revises: 30ee20199668
Create Date: 2023-11-08 13:21:29.705804

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "b46bff422020"
down_revision: Union[str, None] = "30ee20199668"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("users", "admin")


def downgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "admin", sa.BOOLEAN(), autoincrement=False, nullable=False, default=False
        ),
    )
