# pylint: skip-file
"""Se agrego la tabla de intereses, esta tiene un formato de user_id, interes

Revision ID: fac7f52d17c5
Revises: 67e4152de874
Create Date: 2023-10-06 13:19:15.192704

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "fac7f52d17c5"
down_revision: Union[str, None] = "67e4152de874"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "interests",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("interest", sa.String(length=75), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "interest"),
    )


def downgrade() -> None:
    op.drop_table("interests")
