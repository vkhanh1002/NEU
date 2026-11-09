"""Ensure makeup attendance requests have their student reason column."""
import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "0016_repair_attendance_makeup_reason"
down_revision = "0015_attendance_makeup_reason"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()

    if bind.dialect.name == "postgresql":
        table = bind.execute(sa.text("SELECT to_regclass('attendance_makeup_requests')")).scalar_one()
        if table is None:
            raise RuntimeError("attendance_makeup_requests must exist before repairing request_reason")
        op.execute(sa.text(
            "ALTER TABLE attendance_makeup_requests "
            "ADD COLUMN IF NOT EXISTS request_reason TEXT NOT NULL DEFAULT ''"
        ))
        return

    inspector = inspect(bind)
    tables = set(inspector.get_table_names())
    if "attendance_makeup_requests" not in tables:
        raise RuntimeError("attendance_makeup_requests must exist before repairing request_reason")
    columns = {column["name"] for column in inspector.get_columns("attendance_makeup_requests")}
    if "request_reason" not in columns:
        op.add_column(
            "attendance_makeup_requests",
            sa.Column("request_reason", sa.Text(), nullable=False, server_default=""),
        )


def downgrade() -> None:
    # Retain submitted request reasons when rolling the database revision back.
    pass
