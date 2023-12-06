# pylint: skip-file
"""Agrego tablas de post y likes

Revision ID: 1551e9c3c188
Revises: 230e0cb3cef3
Create Date: 2023-10-05 14:28:14.190348

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1551e9c3c188"
down_revision: Union[str, None] = "230e0cb3cef3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    # Drop the 'likes' table
    op.drop_table("likes")

    # Drop the 'posts' table
    op.drop_table("posts")
