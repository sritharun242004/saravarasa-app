"""add profile and test fields

Revision ID: 002_add_profile_and_test_fields
Revises: 001_add_llm_report_fields
Create Date: 2026-06-21
"""
from alembic import op
import sqlalchemy as sa

revision = "002_add_profile_and_test_fields"
down_revision = "001_add_llm_report_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add columns to clients table
    op.add_column("clients", sa.Column("sex", sa.String(), nullable=True))
    op.add_column("clients", sa.Column("profile_completed", sa.Boolean(), server_default="false", nullable=True))
    op.add_column("clients", sa.Column("profile_updated_at", sa.DateTime(timezone=True), nullable=True))

    # Create test_attempts table
    op.create_table(
        "test_attempts",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("client_id", sa.String(), nullable=False),
        sa.Column("test_type", sa.String(), nullable=False),
        sa.Column("challenge_cycle", sa.Integer(), nullable=True),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("status", sa.String(), nullable=True),
        sa.Column("answers", sa.JSON(), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("unlocked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"], ),
        sa.PrimaryKeyConstraint("id"),
        sa.Index("ix_test_attempts_client_id", "client_id"),
    )

    # Create questions table
    op.create_table(
        "questions",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("test_type", sa.String(), nullable=False),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("order", sa.Integer(), nullable=True),
        sa.Column("options", sa.JSON(), nullable=True),
        sa.Column("correct_answer", sa.String(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("questions")
    op.drop_table("test_attempts")
    op.drop_column("clients", "profile_updated_at")
    op.drop_column("clients", "profile_completed")
    op.drop_column("clients", "sex")
