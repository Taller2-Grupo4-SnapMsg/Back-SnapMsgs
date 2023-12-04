# pylint: skip-file

"""Nueva columna de ubicacion

Revision ID: af184bba43bb
Revises: 362ef26c0d9f
Create Date: 2023-09-28 13:56:32.882286

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "af184bba43bb"
down_revision: Union[str, None] = "362ef26c0d9f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
