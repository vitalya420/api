"""first name is nullable

Revision ID: 6bf5daadd1c4
Revises: f97eb1e0e2eb
Create Date: 2024-09-28 17:56:25.370248+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6bf5daadd1c4'
down_revision: Union[str, None] = 'f97eb1e0e2eb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'first_name',
               existing_type=sa.VARCHAR(length=32),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'first_name',
               existing_type=sa.VARCHAR(length=32),
               nullable=False)
    # ### end Alembic commands ###