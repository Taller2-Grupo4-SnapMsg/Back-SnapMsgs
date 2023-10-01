"""se crean las tablas nuevamente, se saca el id del like

Revision ID: a45bb30425a4
Revises: 
Create Date: 2023-09-30 14:29:48.537136

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "a45bb30425a4"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# pylint: disable=C0116
def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    # pylint: disable=E1101
    op.create_table(
        "likes",
        sa.Column("id_post", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id_post", "user_id"),
    )
    # ### end Alembic commands ###


# pylint: disable=C0116
def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    # pylint: disable=E1101
    op.drop_table("likes")
    # ### end Alembic commands ###
