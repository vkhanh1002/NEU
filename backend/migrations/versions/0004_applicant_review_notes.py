"""Store applicant-visible review notes.

Revision ID: 0004_applicant_review_notes
Revises: 0003_student_academics_and_news
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "0004_applicant_review_notes"
down_revision = "0003_student_academics_and_news"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    columns = {column["name"] for column in inspect(bind).get_columns("applicants")}
    if "review_note" not in columns:
        op.add_column(
            "applicants",
            sa.Column("review_note", sa.Text(), server_default=sa.text("''"), nullable=False),
        )


def downgrade() -> None:
    bind = op.get_bind()
    columns = {column["name"] for column in inspect(bind).get_columns("applicants")}
    if "review_note" in columns:
        op.drop_column("applicants", "review_note")
