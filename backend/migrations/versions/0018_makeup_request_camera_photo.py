"""Store a live camera photo and its capture time on makeup requests."""
import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "0018_makeup_request_camera_photo"
down_revision = "0017_post_session_makeup_requests"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    names_and_columns = (
        ("request_photo_path", sa.String(500)),
        ("request_photo_media_type", sa.String(80)),
        ("request_photo_captured_at", sa.DateTime(timezone=True)),
        ("request_photo_received_at", sa.DateTime(timezone=True)),
    )
    if bind.dialect.name == "postgresql":
        schema = bind.execute(sa.text("SELECT current_schema()")).scalar_one()
        preparer = bind.dialect.identifier_preparer
        table = f"{preparer.quote(schema)}.{preparer.quote('attendance_makeup_requests')}"
        columns = {row["name"] for row in inspect(bind).get_columns("attendance_makeup_requests", schema=schema)}
        for name, column_type in names_and_columns:
            if name not in columns:
                op.execute(sa.text(f"ALTER TABLE {table} ADD COLUMN {preparer.quote(name)} {column_type.compile(bind.dialect)} NULL"))
        return

    if "attendance_makeup_requests" not in set(inspect(bind).get_table_names()):
        raise RuntimeError("attendance_makeup_requests must exist before storing request photos")
    columns = {row["name"] for row in inspect(bind).get_columns("attendance_makeup_requests")}
    with op.batch_alter_table("attendance_makeup_requests") as batch:
        for name, column_type in names_and_columns:
            if name not in columns:
                batch.add_column(sa.Column(name, column_type, nullable=True))


def downgrade() -> None:
    # Retain uploaded evidence and capture timestamps during a revision rollback.
    pass
