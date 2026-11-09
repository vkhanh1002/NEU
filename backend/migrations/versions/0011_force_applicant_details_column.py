"""Force applicant details column into the active PostgreSQL schema."""
import sqlalchemy as sa
from alembic import op

revision = "0011_force_applicant_details_column"
down_revision = "0010_repair_applicant_details"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 0010 may already be recorded in databases where its inspector-based
    # repair did not materialize the column. IF NOT EXISTS is safe on fresh DBs.
    op.execute(sa.text("ALTER TABLE applicants ADD COLUMN IF NOT EXISTS details JSON"))
    op.execute(sa.text("UPDATE applicants SET details = '{}'::json WHERE details IS NULL"))
    op.execute(sa.text("ALTER TABLE applicants ALTER COLUMN details SET NOT NULL"))


def downgrade() -> None:
    # Preserve applicant data on downgrade.
    pass
