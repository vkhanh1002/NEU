"""Add student academic records, finance, assignments, news and events.

Revision ID: 0003_student_academics_and_news
Revises: 0002_personnel_attachments
"""
from alembic import op

from app.core.database import Base
from app.models import entities as _entities  # noqa: F401 - registers model tables

revision = "0003_student_academics_and_news"
down_revision = "0002_personnel_attachments"
branch_labels = None
depends_on = None

TABLES = (
    "semesters", "courses", "course_offerings", "course_enrollments", "exams",
    "conduct_records", "student_charges", "payment_transactions", "assignments",
    "assignment_submissions", "news_articles", "university_events",
)


def upgrade() -> None:
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind, tables=[Base.metadata.tables[name] for name in TABLES])


def downgrade() -> None:
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind, tables=[Base.metadata.tables[name] for name in reversed(TABLES)])
