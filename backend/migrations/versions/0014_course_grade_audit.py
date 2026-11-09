"""Store a before/after trail for lecturer score updates."""
import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "0014_course_grade_audit"
down_revision = "0013_smart_attendance"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if "course_grade_audit" not in set(inspect(bind).get_table_names()):
        op.create_table(
        "course_grade_audit",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("enrollment_id", sa.String(36), sa.ForeignKey("course_enrollments.id", ondelete="CASCADE"), nullable=False),
        sa.Column("actor_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("previous_values", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("new_values", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        )
    if "course_grade_audit" in set(inspect(bind).get_table_names()):
        indexes = {row["name"] for row in inspect(bind).get_indexes("course_grade_audit")}
        if "ix_course_grade_audit_enrollment_id" not in indexes:
            op.create_index("ix_course_grade_audit_enrollment_id", "course_grade_audit", ["enrollment_id"])


def downgrade() -> None:
    op.drop_table("course_grade_audit")
