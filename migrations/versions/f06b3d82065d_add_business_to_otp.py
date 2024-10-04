"""add business to otp

Revision ID: f06b3d82065d
Revises: 56a155586ca7
Create Date: 2024-10-03 14:25:48.635703+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f06b3d82065d'
down_revision: Union[str, None] = '56a155586ca7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('otps', sa.Column('business', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('otps', 'business')
    # ### end Alembic commands ###