# pylint: skip-file
"""dropeamos tablas de posts, likes y hashtags

Revision ID: 5caf6a945f4d
Revises: fb0240b2bd48
Create Date: 2023-10-19 23:27:04.307763

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "5caf6a945f4d"
down_revision: Union[str, None] = "fb0240b2bd48"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.drop_table("hashtags")
    op.drop_table("reposts")
    op.drop_table("likes")
    op.drop_table("posts")
    # ### end Alembic commands ###


def downgrade():
    # Define a downgrade method to recreate tables if needed
    op.create_table(
        "posts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("posted_at", sa.DateTime(), default=sa.func.now(), nullable=True),
        sa.Column("content", sa.String(length=1000), nullable=True),
        sa.Column("image", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "reposts",
        sa.Column("id_post", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id_post", "user_id"),
    )

    op.create_table(
        "hashtags",
        sa.Column("id_post", sa.Integer(), nullable=False),
        sa.Column("hashtag", sa.String(length=75), nullable=False),
        sa.PrimaryKeyConstraint("id_post", "hashtag"),
    )

    op.create_table(
        "likes",
        sa.Column("id_post", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["id_post"], ["posts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id_post", "user_id"),
    )
    # ### end Alembic commands ###
