# pylint: skip-file
"""Create new tables (nuevo intento)

Revision ID: 67e4152de874
Revises: ae9fa2844388
Create Date: 2023-10-05 14:54:20.406992

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "67e4152de874"
down_revision: Union[str, None] = "ae9fa2844388"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the 'posts' table
    op.create_table(
        "posts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("posted_at", sa.DateTime(), default=sa.func.now(), nullable=True),
        sa.Column("content", sa.String(length=800), nullable=True),
        sa.Column("image", sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create the 'likes' table
    op.create_table(
        "likes",
        sa.Column("id_post", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["id_post"], ["posts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id_post", "user_id"),
    )


def downgrade() -> None:
    # Drop the 'likes' table
    op.drop_table("likes")

    # Drop the 'posts' table
    op.drop_table("posts")
