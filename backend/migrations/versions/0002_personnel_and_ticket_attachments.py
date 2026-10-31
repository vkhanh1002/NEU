"""Add shared personnel records and support ticket attachments."""
from alembic import op

from app.core.database import Base
from app.models import Personnel, TicketAttachment  # noqa: F401
import app.models  # noqa: F401

revision = "0002_personnel_attachments"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade():
    # Repair any tables missed by an interrupted or previously stamped baseline
    # before adding attachments (which reference users and support_tickets).
    Base.metadata.create_all(bind=op.get_bind(), checkfirst=True)


def downgrade():
    TicketAttachment.__table__.drop(bind=op.get_bind(), checkfirst=True)
    Personnel.__table__.drop(bind=op.get_bind(), checkfirst=True)
