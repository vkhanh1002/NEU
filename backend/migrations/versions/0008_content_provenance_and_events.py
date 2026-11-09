"""Store sources and distinguish all-day events."""
import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "0008_content_provenance_and_events"
down_revision = "0007_knowledge_source_registry"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    tables = set(inspect(bind).get_table_names())
    # Older Alembic versions created this column as VARCHAR(32). Expand it
    # before Alembic writes this revision ID at the end of the migration.
    if "alembic_version" in tables:
        version_column = next(
            (column for column in inspect(bind).get_columns("alembic_version")
             if column["name"] == "version_num"),
            None,
        )
        if version_column is not None:
            current_length = getattr(version_column["type"], "length", None)
            if current_length is not None and current_length < 128:
                op.alter_column(
                    "alembic_version", "version_num",
                    existing_type=version_column["type"],
                    type_=sa.String(length=128),
                    existing_nullable=version_column["nullable"],
                )
    if "news_articles" in tables:
        columns = {column["name"] for column in inspect(bind).get_columns("news_articles")}
        if "source_url" not in columns:
            op.add_column("news_articles", sa.Column("source_url", sa.String(500), nullable=False, server_default=""))
        # These are the known generic demo rows created by the former seed. Keep
        # them in the database for auditability, but remove them from public news.
        op.execute(sa.text("""
            UPDATE news_articles SET status = 'archived'
            WHERE slug IN (
                'lap-ke-hoach-hoc-tap', 'doc-tai-lieu-hieu-qua', 'ky-nang-thuyet-trinh',
                'tim-kiem-thong-tin', 'chuan-bi-ho-so', 'hoi-dap-tu-van', 'ket-noi-cong-dong',
                'bao-ve-suc-khoe-hoc-duong', 'su-dung-tro-ly-so', 'ky-nang-lam-viec-nhom',
                'huong-dan-su-dung-cong-sinh-vien'
            ) AND status = 'published'
        """))
    if "university_events" in tables:
        columns = {column["name"] for column in inspect(bind).get_columns("university_events")}
        if "source_url" not in columns:
            op.add_column("university_events", sa.Column("source_url", sa.String(500), nullable=False, server_default=""))
        if "is_all_day" not in columns:
            op.add_column("university_events", sa.Column("is_all_day", sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade() -> None:
    bind = op.get_bind()
    tables = set(inspect(bind).get_table_names())
    if "university_events" in tables:
        columns = {column["name"] for column in inspect(bind).get_columns("university_events")}
        if "is_all_day" in columns:
            op.drop_column("university_events", "is_all_day")
        if "source_url" in columns:
            op.drop_column("university_events", "source_url")
    if "news_articles" in tables:
        columns = {column["name"] for column in inspect(bind).get_columns("news_articles")}
        if "source_url" in columns:
            op.drop_column("news_articles", "source_url")
