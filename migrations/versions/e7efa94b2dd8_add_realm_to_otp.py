"""add realm to otp

Revision ID: e7efa94b2dd8
Revises: 6a13a57480b8
Create Date: 2024-10-09 14:36:51.909713+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e7efa94b2dd8'
down_revision: Union[str, None] = '6a13a57480b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('otps', sa.Column('realm', sa.Enum('web', 'mobile', name='realm'), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('otps', 'realm')
    # ### end Alembic commands ###