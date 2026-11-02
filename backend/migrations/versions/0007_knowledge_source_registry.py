"""Track provenance and content hashes for local knowledge imports."""
import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "0007_knowledge_source_registry"
down_revision = "0006_guest_chat_public_knowledge"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    tables = set(inspect(bind).get_table_names())
    if "knowledge_documents" not in tables:
        return
    columns = {column["name"] for column in inspect(bind).get_columns("knowledge_documents")}
    for name, column in (
        ("source_path", sa.Column("source_path", sa.String(500), nullable=True)),
        ("content_hash", sa.Column("content_hash", sa.String(64), nullable=True)),
        ("source_status", sa.Column("source_status", sa.String(30), nullable=True)),
        ("source_year", sa.Column("source_year", sa.Integer(), nullable=True)),
    ):
        if name not in columns:
            op.add_column("knowledge_documents", column)
    indexes = {item["name"] for item in inspect(bind).get_indexes("knowledge_documents")}
    if "uq_knowledge_documents_source_path" not in indexes:
        op.create_index("uq_knowledge_documents_source_path", "knowledge_documents", ["source_path"], unique=True)


def downgrade() -> None:
    bind = op.get_bind()
    if "knowledge_documents" not in set(inspect(bind).get_table_names()):
        return
    columns = {column["name"] for column in inspect(bind).get_columns("knowledge_documents")}
    indexes = {item["name"] for item in inspect(bind).get_indexes("knowledge_documents")}
    if "uq_knowledge_documents_source_path" in indexes:
        op.drop_index("uq_knowledge_documents_source_path", table_name="knowledge_documents")
    for name in ("source_year", "source_status", "content_hash", "source_path"):
        if name in columns:
            op.drop_column("knowledge_documents", name)
