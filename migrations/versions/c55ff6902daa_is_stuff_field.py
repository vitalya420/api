"""is stuff field

Revision ID: c55ff6902daa
Revises: b7b059898b76
Create Date: 2024-10-11 16:14:30.896030+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c55ff6902daa'
down_revision: Union[str, None] = 'b7b059898b76'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('clients', sa.Column('is_staff', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('clients', 'is_staff')
    # ### end Alembic commands ###
