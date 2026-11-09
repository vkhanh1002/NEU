"""Store student reasons on makeup attendance requests."""
import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "0015_attendance_makeup_reason"
down_revision = "0014_course_grade_audit"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if "attendance_makeup_requests" not in set(inspect(bind).get_table_names()):
        return
    columns = {row["name"] for row in inspect(bind).get_columns("attendance_makeup_requests")}
    if "request_reason" not in columns:
        op.add_column("attendance_makeup_requests", sa.Column(
            "request_reason", sa.Text(), nullable=False, server_default="",
        ))


def downgrade() -> None:
    inspector = inspect(op.get_bind())
    if "attendance_makeup_requests" not in set(inspector.get_table_names()):
        return
    columns = {row["name"] for row in inspector.get_columns("attendance_makeup_requests")}
    if "request_reason" in columns:
        op.drop_column("attendance_makeup_requests", "request_reason")
