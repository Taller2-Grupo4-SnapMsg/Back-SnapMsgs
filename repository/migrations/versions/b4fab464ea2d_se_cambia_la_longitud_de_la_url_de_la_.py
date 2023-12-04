# pylint: skip-file
"""se cambia la longitud de la url de la imagen en la tabla de posts

Revision ID: b4fab464ea2d
Revises: fac7f52d17c5
Create Date: 2023-10-08 00:27:22.346125

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "b4fab464ea2d"
down_revision: Union[str, None] = "fac7f52d17c5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Cambia el tipo de columna 'image' a String()
    op.alter_column("posts", "image", type_=sa.String(), existing_nullable=True)


def downgrade():
    # Revierte el cambio y vuelve a establecer el tipo de columna 'image' como String(100)
    op.alter_column(
        "posts", "image", type_=sa.String(length=100), existing_nullable=True
    )
