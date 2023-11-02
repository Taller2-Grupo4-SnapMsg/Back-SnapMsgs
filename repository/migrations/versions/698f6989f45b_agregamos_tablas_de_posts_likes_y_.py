# pylint: skip-file
"""agregamos tablas de posts, likes y hashtags-si va

Revision ID: 698f6989f45b
Revises: 2f5a0ebd6f23
Create Date: 2023-10-19 23:54:38.941213

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "698f6989f45b"
down_revision: Union[str, None] = "2f5a0ebd6f23"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the 'contents' table
    op.create_table(
        "contents",
        sa.Column("content_id", sa.Integer(), nullable=False),
        sa.Column("text", sa.String(length=1000), nullable=True),
        sa.Column("image", sa.String(length=1000), nullable=True),
        sa.PrimaryKeyConstraint("content_id"),
    )

    # Crea la tabla "posts"
    op.create_table(
        "posts",
        sa.Column("post_id", sa.Integer(), nullable=False),
        sa.Column("user_poster_id", sa.Integer(), nullable=False),
        sa.Column("user_creator_id", sa.Integer(), nullable=False),
        sa.Column("content_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(
            ["content_id"],
            ["contents.content_id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_creator_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_poster_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("post_id"),
    )

    # Crea la tabla "likes"
    op.create_table(
        "likes",
        sa.Column("content_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), default=sa.func.now(), nullable=True),
        sa.UniqueConstraint("user_id", "content_id"),
        sa.ForeignKeyConstraint(
            ["content_id"],
            ["contents.content_id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("content_id", "user_id"),
    )

    # Crea la tabla "hashtags"
    op.create_table(
        "hashtags",
        sa.Column("content_id", sa.Integer(), nullable=False),
        sa.Column("hashtag", sa.String(length=75), nullable=False),
        sa.Column("created_at", sa.DateTime(), default=sa.func.now(), nullable=True),
        sa.UniqueConstraint("content_id", "hashtag"),
        sa.ForeignKeyConstraint(
            ["content_id"],
            ["contents.content_id"],
        ),
        sa.PrimaryKeyConstraint("content_id", "hashtag"),
    )


def downgrade() -> None:
    op.drop_table("hashtags")

    # Drop the 'likes' table
    op.drop_table("likes")

    # Drop the 'posts' table
    op.drop_table("posts")

    # Drop the 'contents' table
    op.drop_table("contents")
