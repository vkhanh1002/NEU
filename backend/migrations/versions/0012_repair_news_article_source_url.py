"""Ensure news article provenance column exists on upgraded databases."""
import sqlalchemy as sa
from alembic import op

revision = "0012_repair_news_article_source_url"
down_revision = "0011_force_applicant_details_column"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Some existing databases reached the current head without the column
    # expected by NewsArticle and the seed. Preserve existing rows and make
    # the migration safe for fresh databases where it is already present.
    op.execute(sa.text(
        "ALTER TABLE news_articles "
        "ADD COLUMN IF NOT EXISTS source_url VARCHAR(500) NOT NULL DEFAULT ''"
    ))


def downgrade() -> None:
    # Keep source provenance data when rolling back application migrations.
    pass
