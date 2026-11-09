"""Allow students to request makeup attendance after a session closes."""
import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "0017_post_session_makeup_requests"
down_revision = "0016_repair_attendance_makeup_reason"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        schema = bind.execute(sa.text("SELECT current_schema()")).scalar_one()
        preparer = bind.dialect.identifier_preparer
        table = f"{preparer.quote(schema)}.{preparer.quote('attendance_makeup_requests')}"
        columns = {
            row["name"]: row
            for row in inspect(bind).get_columns("attendance_makeup_requests", schema=schema)
        }
        if "request_reason" not in columns:
            op.execute(sa.text(
                f"ALTER TABLE {table} ADD COLUMN request_reason TEXT NOT NULL DEFAULT ''"
            ))
        if columns.get("evidence_id", {}).get("nullable") is False:
            op.execute(sa.text(f"ALTER TABLE {table} ALTER COLUMN evidence_id DROP NOT NULL"))
        return

    inspector = inspect(bind)
    if "attendance_makeup_requests" not in set(inspector.get_table_names()):
        raise RuntimeError("attendance_makeup_requests must exist before enabling makeup requests")
    columns = {row["name"]: row for row in inspector.get_columns("attendance_makeup_requests")}
    with op.batch_alter_table("attendance_makeup_requests") as batch:
        if "request_reason" not in columns:
            batch.add_column(sa.Column("request_reason", sa.Text(), nullable=False, server_default=""))
        if columns.get("evidence_id", {}).get("nullable") is False:
            batch.alter_column("evidence_id", existing_type=sa.String(36), nullable=True)


def downgrade() -> None:
    # Keep optional evidence and submitted reasons to avoid discarding user requests.
    pass
