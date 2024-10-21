"""work schedule

Revision ID: 1d390e0272fc
Revises: 2e8888bfe778
Create Date: 2024-10-21 16:22:39.971640+00:00

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "1d390e0272fc"
down_revision: Union[str, None] = "2e8888bfe778"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "day_schedule_infos",
        sa.Column("open_time", sa.Time(), nullable=True),
        sa.Column("close_time", sa.Time(), nullable=True),
        sa.Column("is_day_off", sa.Boolean(), nullable=True),
        sa.Column("has_lunch_break", sa.Boolean(), nullable=True),
        sa.Column("lunch_break_start", sa.Time(), nullable=True),
        sa.Column("lunch_break_end", sa.Time(), nullable=True),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "establishment_work_schedules",
        sa.Column("establishment_id", sa.Integer(), nullable=False),
        sa.Column("monday_id", sa.Integer(), nullable=False),
        sa.Column("tuesday_id", sa.Integer(), nullable=False),
        sa.Column("wednesday_id", sa.Integer(), nullable=False),
        sa.Column("thursday_id", sa.Integer(), nullable=False),
        sa.Column("friday_id", sa.Integer(), nullable=False),
        sa.Column("saturday_id", sa.Integer(), nullable=False),
        sa.Column("sunday_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.ForeignKeyConstraint(
            ["establishment_id"], ["establishments.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["friday_id"],
            ["day_schedule_infos.id"],
        ),
        sa.ForeignKeyConstraint(
            ["monday_id"],
            ["day_schedule_infos.id"],
        ),
        sa.ForeignKeyConstraint(
            ["saturday_id"],
            ["day_schedule_infos.id"],
        ),
        sa.ForeignKeyConstraint(
            ["sunday_id"],
            ["day_schedule_infos.id"],
        ),
        sa.ForeignKeyConstraint(
            ["thursday_id"],
            ["day_schedule_infos.id"],
        ),
        sa.ForeignKeyConstraint(
            ["tuesday_id"],
            ["day_schedule_infos.id"],
        ),
        sa.ForeignKeyConstraint(
            ["wednesday_id"],
            ["day_schedule_infos.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.drop_table("work_schedules")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "work_schedules",
        sa.Column(
            "establishment_id", sa.INTEGER(), autoincrement=False, nullable=False
        ),
        sa.Column(
            "day_of_week",
            postgresql.ENUM(
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
                name="dayofweek",
            ),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column("open_time", postgresql.TIME(), autoincrement=False, nullable=True),
        sa.Column("close_time", postgresql.TIME(), autoincrement=False, nullable=True),
        sa.Column("is_day_off", sa.BOOLEAN(), autoincrement=False, nullable=True),
        sa.Column("has_lunch_break", sa.BOOLEAN(), autoincrement=False, nullable=True),
        sa.Column(
            "lunch_break_start", postgresql.TIME(), autoincrement=False, nullable=True
        ),
        sa.Column(
            "lunch_break_end", postgresql.TIME(), autoincrement=False, nullable=True
        ),
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.ForeignKeyConstraint(
            ["establishment_id"],
            ["establishments.id"],
            name="work_schedules_establishment_id_fkey",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="work_schedules_pkey"),
    )
    op.drop_table("establishment_work_schedules")
    op.drop_table("day_schedule_infos")
    # ### end Alembic commands ###
