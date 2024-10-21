"""fix

Revision ID: 936c0592da57
Revises: 9eaf8a4c75ea
Create Date: 2024-10-19 13:21:04.412964+00:00

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "936c0592da57"
down_revision: Union[str, None] = "9eaf8a4c75ea"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "addresses",
        sa.Column("address", sa.String(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "establishments",
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("image", sa.String(length=128), nullable=True),
        sa.Column("address_id", sa.Integer(), nullable=True),
        sa.Column("business_code", sa.String(), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.ForeignKeyConstraint(
            ["address_id"],
            ["addresses.id"],
        ),
        sa.ForeignKeyConstraint(
            ["business_code"], ["businesses.code"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "work_schedules",
        sa.Column("establishment_id", sa.Integer(), nullable=False),
        sa.Column(
            "day_of_week",
            sa.Enum(
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
                name="dayofweek",
            ),
            nullable=False,
        ),
        sa.Column("open_time", sa.Time(), nullable=True),
        sa.Column("close_time", sa.Time(), nullable=True),
        sa.Column("is_day_off", sa.Boolean(), nullable=True),
        sa.Column("has_lunch_break", sa.Boolean(), nullable=True),
        sa.Column("lunch_break_start", sa.Time(), nullable=True),
        sa.Column("lunch_break_end", sa.Time(), nullable=True),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.ForeignKeyConstraint(
            ["establishment_id"], ["establishments.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("work_schedules")
    op.drop_table("establishments")
    op.drop_table("addresses")
    # ### end Alembic commands ###
