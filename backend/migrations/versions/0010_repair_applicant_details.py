"""Ensure applicant JSON details exists and is populated."""
import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "0010_repair_applicant_details"
down_revision = "0009_admission_workflow"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if "applicants" not in set(inspect(bind).get_table_names()):
        return
    columns = {column["name"]: column for column in inspect(bind).get_columns("applicants")}
    if "details" not in columns:
        op.add_column("applicants", sa.Column("details", sa.JSON(), nullable=True))
    op.execute(sa.text("UPDATE applicants SET details = '{}' WHERE details IS NULL"))
    column = next(column for column in inspect(bind).get_columns("applicants") if column["name"] == "details")
    if column["nullable"]:
        op.alter_column("applicants", "details", existing_type=column["type"], nullable=False)


def downgrade() -> None:
    # Keep applicant details intact during downgrade; it is part of the model
    # and removing the column would discard applicant data.
    pass
