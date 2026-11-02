"""Add admission, kb, and feedback tables."""
from alembic import op
import sqlalchemy as sa
from app.core.database import Base
import app.models  # noqa: F401

revision = "0003_admission_kb_feedback"
down_revision = "0002_personnel_attachments"
branch_labels = None
depends_on = None


def upgrade():
    # Create any newly added tables
    Base.metadata.create_all(bind=op.get_bind(), checkfirst=True)
    
    # In case knowledge_documents already existed in postgres, add new columns if not present
    conn = op.get_bind()
    doc_cols = [
        ("title", "VARCHAR(255) DEFAULT '' NOT NULL"),
        ("source_type", "VARCHAR(50) DEFAULT 'document' NOT NULL"),
        ("source_url", "VARCHAR(500) DEFAULT '' NOT NULL"),
        ("audience", "VARCHAR(50) DEFAULT 'chung' NOT NULL"),
        ("category", "VARCHAR(80) DEFAULT 'tuyển sinh' NOT NULL"),
        ("department_id", "VARCHAR(36) REFERENCES departments(id)"),
        ("academic_year", "VARCHAR(30) DEFAULT '2025-2026' NOT NULL"),
        ("effective_from", "DATE"),
        ("effective_to", "DATE"),
        ("version", "VARCHAR(30) DEFAULT '1.0' NOT NULL"),
        ("checksum", "VARCHAR(64) DEFAULT '' NOT NULL"),
    ]
    for col_name, col_def in doc_cols:
        try:
            conn.execute(sa.text(f"ALTER TABLE knowledge_documents ADD COLUMN IF NOT EXISTS {col_name} {col_def};"))
        except Exception:
            pass

    chunk_cols = [
        ("heading_path", "VARCHAR(300) DEFAULT '' NOT NULL"),
        ("page_number", "INTEGER"),
        ("token_count", "INTEGER DEFAULT 0 NOT NULL"),
        ("chunk_metadata", "JSON DEFAULT '{}'::json NOT NULL"),
    ]
    for col_name, col_def in chunk_cols:
        try:
            conn.execute(sa.text(f"ALTER TABLE knowledge_chunks ADD COLUMN IF NOT EXISTS {col_name} {col_def};"))
        except Exception:
            pass


def downgrade():
    pass
