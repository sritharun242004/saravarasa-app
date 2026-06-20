"""add llm report fields to challenge_reports

Revision ID: 001_add_llm_report_fields
Revises:
Create Date: 2026-06-19
"""
from alembic import op
import sqlalchemy as sa

revision = "001_add_llm_report_fields"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("challenge_reports", sa.Column("commitment_level", sa.String(), nullable=True))
    op.add_column("challenge_reports", sa.Column("commitment_analysis", sa.Text(), nullable=True))
    op.add_column("challenge_reports", sa.Column("food_recommendations", sa.JSON(), nullable=True))
    op.add_column("challenge_reports", sa.Column("llm_insights", sa.JSON(), nullable=True))
    op.add_column("challenge_reports", sa.Column("llm_summary", sa.Text(), nullable=True))
    op.add_column("challenge_reports", sa.Column("llm_generated_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("challenge_reports", "llm_generated_at")
    op.drop_column("challenge_reports", "llm_summary")
    op.drop_column("challenge_reports", "llm_insights")
    op.drop_column("challenge_reports", "food_recommendations")
    op.drop_column("challenge_reports", "commitment_analysis")
    op.drop_column("challenge_reports", "commitment_level")
