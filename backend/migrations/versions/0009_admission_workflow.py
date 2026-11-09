"""Structured applicant details, ordered preferences, and protected files."""
import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "0009_admission_workflow"
down_revision = "0008_content_provenance_and_events"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    tables = set(inspect(bind).get_table_names())
    if "applicants" in tables:
        columns = {column["name"] for column in inspect(bind).get_columns("applicants")}
        if "details" not in columns:
            op.add_column("applicants", sa.Column("details", sa.JSON(), nullable=True))
            op.execute(sa.text("UPDATE applicants SET details = '{}' WHERE details IS NULL"))

    if "applicant_preferences" not in tables:
        op.create_table(
            "applicant_preferences",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("applicant_id", sa.String(36), sa.ForeignKey("applicants.id", ondelete="CASCADE"), nullable=False),
            sa.Column("major_id", sa.String(36), sa.ForeignKey("majors.id"), nullable=False),
            sa.Column("preference_order", sa.Integer(), nullable=False),
            sa.Column("program_name", sa.String(180), server_default="", nullable=False),
            sa.Column("admission_method", sa.String(100), server_default="", nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
            sa.UniqueConstraint("applicant_id", "preference_order", name="uq_applicant_preference_order"),
            sa.UniqueConstraint("applicant_id", "major_id", name="uq_applicant_preference_major"),
        )
        op.create_index("ix_applicant_preferences_applicant_id", "applicant_preferences", ["applicant_id"])
        op.create_index("ix_applicant_preferences_major_id", "applicant_preferences", ["major_id"])

    if "applicant_documents" not in tables:
        op.create_table(
            "applicant_documents",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("applicant_id", sa.String(36), sa.ForeignKey("applicants.id", ondelete="CASCADE"), nullable=False),
            sa.Column("uploaded_by", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("document_type", sa.String(100), nullable=False),
            sa.Column("filename", sa.String(255), nullable=False),
            sa.Column("media_type", sa.String(120), nullable=False),
            sa.Column("size_bytes", sa.Integer(), nullable=False),
            sa.Column("content", sa.LargeBinary(), nullable=False),
            sa.Column("status", sa.String(30), server_default="Chờ kiểm tra", nullable=False),
            sa.Column("review_note", sa.String(1000), server_default="", nullable=False),
            sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("reviewed_by", sa.String(36), sa.ForeignKey("users.id"), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        )
        op.create_index("ix_applicant_documents_applicant_id", "applicant_documents", ["applicant_id"])
        op.create_index("ix_applicant_documents_status", "applicant_documents", ["status"])
        op.create_index("ix_applicant_documents_applicant_status", "applicant_documents", ["applicant_id", "status"])


def downgrade() -> None:
    bind = op.get_bind()
    tables = set(inspect(bind).get_table_names())
    if "applicant_documents" in tables:
        op.drop_table("applicant_documents")
    if "applicant_preferences" in tables:
        op.drop_table("applicant_preferences")
    if "applicants" in tables and "details" in {column["name"] for column in inspect(bind).get_columns("applicants")}:
        op.drop_column("applicants", "details")
