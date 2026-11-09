"""Add session based attendance, camera evidence, requests and audit history."""
import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "0013_smart_attendance"
down_revision = "0012_repair_news_article_source_url"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = set(inspector.get_table_names())
    if "attendance_sessions" not in tables:
        op.create_table(
        "attendance_sessions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("offering_id", sa.String(36), sa.ForeignKey("course_offerings.id", ondelete="CASCADE"), nullable=False),
        sa.Column("opened_by", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="open"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        )
    _ensure_index("ix_attendance_sessions_offering_id", "attendance_sessions", ["offering_id"])
    _ensure_index("ix_attendance_sessions_status", "attendance_sessions", ["status"])

    if "attendance_records" not in tables:
        op.create_table(
        "attendance_records",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("session_id", sa.String(36), sa.ForeignKey("attendance_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("student_id", sa.String(36), sa.ForeignKey("students.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="absent"),
        sa.Column("marked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("marked_by", sa.String(36), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("session_id", "student_id", name="uq_attendance_session_student"),
        )
    _ensure_index("ix_attendance_records_session_id", "attendance_records", ["session_id"])
    _ensure_index("ix_attendance_records_student_id", "attendance_records", ["student_id"])

    if "attendance_evidence" not in tables:
        op.create_table(
        "attendance_evidence",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("session_id", sa.String(36), sa.ForeignKey("attendance_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("student_id", sa.String(36), sa.ForeignKey("students.id", ondelete="CASCADE"), nullable=False),
        sa.Column("storage_path", sa.String(500), nullable=False),
        sa.Column("media_type", sa.String(80), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("session_id", "student_id", name="uq_attendance_evidence_session_student"),
        )
    _ensure_index("ix_attendance_evidence_session_id", "attendance_evidence", ["session_id"])
    _ensure_index("ix_attendance_evidence_student_id", "attendance_evidence", ["student_id"])

    if "attendance_makeup_requests" not in tables:
        op.create_table(
        "attendance_makeup_requests",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("record_id", sa.String(36), sa.ForeignKey("attendance_records.id", ondelete="CASCADE"), nullable=False),
        sa.Column("evidence_id", sa.String(36), sa.ForeignKey("attendance_evidence.id"), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewed_by", sa.String(36), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("review_reason", sa.String(1000), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("record_id", name="uq_attendance_makeup_record"),
        )
    _ensure_index("ix_attendance_makeup_requests_record_id", "attendance_makeup_requests", ["record_id"])
    _ensure_index("ix_attendance_makeup_requests_status", "attendance_makeup_requests", ["status"])

    if "attendance_audit_logs" not in tables:
        op.create_table(
        "attendance_audit_logs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("session_id", sa.String(36), sa.ForeignKey("attendance_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("record_id", sa.String(36), sa.ForeignKey("attendance_records.id", ondelete="SET NULL"), nullable=True),
        sa.Column("actor_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("action", sa.String(40), nullable=False),
        sa.Column("details", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        )
    _ensure_index("ix_attendance_audit_logs_session_id", "attendance_audit_logs", ["session_id"])
    _ensure_index("ix_attendance_audit_logs_record_id", "attendance_audit_logs", ["record_id"])


def _ensure_index(name: str, table: str, columns: list[str]) -> None:
    inspector = inspect(op.get_bind())
    if table in inspector.get_table_names() and name not in {row["name"] for row in inspector.get_indexes(table)}:
        op.create_index(name, table, columns)


def downgrade() -> None:
    op.drop_table("attendance_audit_logs")
    op.drop_table("attendance_makeup_requests")
    op.drop_table("attendance_evidence")
    op.drop_table("attendance_records")
    op.drop_table("attendance_sessions")
