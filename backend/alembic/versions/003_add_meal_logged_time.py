"""add logged_time to meal_logs

Revision ID: 003_add_meal_logged_time
Revises: 002_add_profile_and_test_fields
Create Date: 2026-07-01
"""
from alembic import op
import sqlalchemy as sa

revision = "003_add_meal_logged_time"
down_revision = "002_add_profile_and_test_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("meal_logs", sa.Column("logged_time", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("meal_logs", "logged_time")
