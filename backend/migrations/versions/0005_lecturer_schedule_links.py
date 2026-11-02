"""Link lecturer logins to personnel and add course offering notes."""
import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "0005_lecturer_schedule_links"
down_revision = "0004_applicant_review_notes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    tables = set(inspect(bind).get_table_names())
    if "personnel" in tables:
        columns = {column["name"] for column in inspect(bind).get_columns("personnel")}
        if "user_id" not in columns:
            with op.batch_alter_table("personnel") as batch:
                batch.add_column(sa.Column("user_id", sa.String(length=36), nullable=True))
                batch.create_foreign_key("fk_personnel_user_id_users", "users", ["user_id"], ["id"], ondelete="SET NULL")
                batch.create_unique_constraint("uq_personnel_user_id", ["user_id"])
    if "course_offerings" in tables:
        columns = {column["name"] for column in inspect(bind).get_columns("course_offerings")}
        if "note" not in columns:
            op.add_column("course_offerings", sa.Column("note", sa.String(length=500), server_default="", nullable=False))


def downgrade() -> None:
    bind = op.get_bind()
    tables = set(inspect(bind).get_table_names())
    if "personnel" in tables:
        columns = {column["name"] for column in inspect(bind).get_columns("personnel")}
        if "user_id" in columns:
            with op.batch_alter_table("personnel") as batch:
                batch.drop_constraint("fk_personnel_user_id_users", type_="foreignkey")
                batch.drop_constraint("uq_personnel_user_id", type_="unique")
                batch.drop_column("user_id")
    if "course_offerings" in tables:
        columns = {column["name"] for column in inspect(bind).get_columns("course_offerings")}
        if "note" in columns:
            op.drop_column("course_offerings", "note")
