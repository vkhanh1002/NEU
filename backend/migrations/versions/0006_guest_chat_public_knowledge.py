"""Persist isolated guest chat sessions and mark public knowledge documents."""
import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "0006_guest_chat_public_knowledge"
down_revision = "0005_lecturer_schedule_links"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    tables = set(inspect(bind).get_table_names())
    if "knowledge_documents" in tables and "is_public" not in {c["name"] for c in inspect(bind).get_columns("knowledge_documents")}:
        op.add_column("knowledge_documents", sa.Column("is_public", sa.Boolean(), server_default=sa.false(), nullable=False))
    if "guest_chat_sessions" not in tables:
        op.create_table(
            "guest_chat_sessions",
            sa.Column("token_hash", sa.String(64), primary_key=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        )
    if "guest_chat_messages" not in tables:
        op.create_table(
            "guest_chat_messages",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("session_hash", sa.String(64), sa.ForeignKey("guest_chat_sessions.token_hash", ondelete="CASCADE"), nullable=False),
            sa.Column("role", sa.String(20), nullable=False),
            sa.Column("content", sa.Text(), nullable=False),
            sa.Column("sources", sa.JSON(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        )
        op.create_index("ix_guest_chat_messages_session_hash", "guest_chat_messages", ["session_hash"])


def downgrade() -> None:
    bind = op.get_bind()
    tables = set(inspect(bind).get_table_names())
    if "guest_chat_messages" in tables:
        op.drop_index("ix_guest_chat_messages_session_hash", table_name="guest_chat_messages")
        op.drop_table("guest_chat_messages")
    if "guest_chat_sessions" in tables:
        op.drop_table("guest_chat_sessions")
    if "knowledge_documents" in tables and "is_public" in {c["name"] for c in inspect(bind).get_columns("knowledge_documents")}:
        op.drop_column("knowledge_documents", "is_public")
