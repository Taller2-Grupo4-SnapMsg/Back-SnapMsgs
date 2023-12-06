# pylint: skip-file
"""agrego nuevas tablas (intento 2)

Revision ID: 8aca63428a6b
Revises: 1551e9c3c188
Create Date: 2023-10-05 14:38:48.820362

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8aca63428a6b"
down_revision: Union[str, None] = "1551e9c3c188"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    # Drop the 'likes' table
    op.drop_table("likes")

    # Drop the 'posts' table
    op.drop_table("posts")
