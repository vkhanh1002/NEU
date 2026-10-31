from datetime import date, datetime, timezone
from uuid import uuid4

from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Index, Integer, JSON, LargeBinary, String, Text
from sqlalchemy.orm import Mapped, deferred, mapped_column, relationship

from app.core.database import Base


def new_id() -> str:
    return str(uuid4())


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc, nullable=False)


class Faculty(TimestampMixin, Base):
    __tablename__ = "faculties"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(160), unique=True, nullable=False)
    majors: Mapped[list["Major"]] = relationship(back_populates="faculty")


class Major(TimestampMixin, Base):
    __tablename__ = "majors"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(180), index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    faculty_id: Mapped[str] = mapped_column(ForeignKey("faculties.id"), index=True, nullable=False)
    duration_years: Mapped[int] = mapped_column(Integer, default=4, nullable=False)
    tuition_per_year_vnd: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    admission_quota: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    admission_status: Mapped[str] = mapped_column(String(30), default="Đang tuyển sinh", nullable=False)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    faculty: Mapped[Faculty] = relationship(back_populates="majors")


class User(TimestampMixin, Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(180), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(40), default="student", index=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Notification(TimestampMixin, Base):
    __tablename__ = "notifications"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    message: Mapped[str] = mapped_column(String(500), nullable=False)
    href: Mapped[str] = mapped_column(String(300), default="/support", nullable=False)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Applicant(TimestampMixin, Base):
    __tablename__ = "applicants"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    email: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(180), nullable=False)
    phone: Mapped[str] = mapped_column(String(40), default="", nullable=False)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    address: Mapped[str] = mapped_column(String(500), default="", nullable=False)
    desired_major_id: Mapped[str] = mapped_column(ForeignKey("majors.id"), index=True, nullable=False)
    admission_method: Mapped[str] = mapped_column(String(100), default="Học bạ (demo)", nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="Mới tiếp nhận", index=True, nullable=False)
    student_id: Mapped[str | None] = mapped_column(ForeignKey("students.id"), nullable=True, unique=True)
    major: Mapped[Major] = relationship()


class Student(TimestampMixin, Base):
    __tablename__ = "students"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True, unique=True)
    applicant_id: Mapped[str | None] = mapped_column(ForeignKey("applicants.id"), nullable=True, unique=True)
    student_number: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(180), nullable=False)
    email: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(40), default="", nullable=False)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    gender: Mapped[str] = mapped_column(String(30), default="Chưa cập nhật", nullable=False)
    address: Mapped[str] = mapped_column(String(500), default="", nullable=False)
    major_id: Mapped[str] = mapped_column(ForeignKey("majors.id"), index=True, nullable=False)
    cohort: Mapped[str] = mapped_column(String(30), default="2026", nullable=False)
    class_name: Mapped[str] = mapped_column(String(60), default="", nullable=False)
    study_status: Mapped[str] = mapped_column(String(40), default="Đang học", index=True, nullable=False)
    enrollment_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    emergency_contact: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    user: Mapped[User | None] = relationship()
    major: Mapped[Major] = relationship()


class Personnel(TimestampMixin, Base):
    """Shared employee record for academic staff and university employees."""
    __tablename__ = "personnel"
    __table_args__ = (
        Index("ix_personnel_type_status", "kind", "work_status"),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    code: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)
    kind: Mapped[str] = mapped_column(String(30), index=True, nullable=False)  # lecturer | employee
    full_name: Mapped[str] = mapped_column(String(180), index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(40), default="", nullable=False)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    gender: Mapped[str] = mapped_column(String(30), default="Chưa cập nhật", nullable=False)
    address: Mapped[str] = mapped_column(String(500), default="", nullable=False)
    avatar_url: Mapped[str] = mapped_column(String(500), default="", nullable=False)
    education_level: Mapped[str] = mapped_column(String(120), default="", nullable=False)
    academic_rank: Mapped[str] = mapped_column(String(120), default="", nullable=False)
    specialty: Mapped[str] = mapped_column(String(240), default="", nullable=False)
    faculty_id: Mapped[str | None] = mapped_column(ForeignKey("faculties.id"), index=True, nullable=True)
    department: Mapped[str] = mapped_column(String(180), default="", index=True, nullable=False)
    position: Mapped[str] = mapped_column(String(160), default="", nullable=False)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    work_status: Mapped[str] = mapped_column(String(40), default="Đang công tác", index=True, nullable=False)
    notes: Mapped[str] = mapped_column(Text, default="", nullable=False)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    faculty: Mapped[Faculty | None] = relationship()


class SupportTicket(TimestampMixin, Base):
    __tablename__ = "support_tickets"
    __table_args__ = (Index("ix_tickets_owner_status", "owner_id", "status"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    code: Mapped[str] = mapped_column(String(24), unique=True, index=True, nullable=False)
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(80), nullable=False)
    subject: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[str] = mapped_column(String(30), default="Bình thường", nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="Mới tiếp nhận", index=True, nullable=False)
    assignee_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    satisfaction_rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    satisfaction_feedback: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    owner: Mapped[User] = relationship(foreign_keys=[owner_id])
    messages: Mapped[list["TicketMessage"]] = relationship(back_populates="ticket", cascade="all, delete-orphan", order_by="TicketMessage.created_at")
    attachments: Mapped[list["TicketAttachment"]] = relationship(cascade="all, delete-orphan", order_by="TicketAttachment.created_at")


class TicketMessage(TimestampMixin, Base):
    __tablename__ = "ticket_messages"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    ticket_id: Mapped[str] = mapped_column(ForeignKey("support_tickets.id", ondelete="CASCADE"), index=True, nullable=False)
    author_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    ticket: Mapped[SupportTicket] = relationship(back_populates="messages")
    author: Mapped[User] = relationship()


class TicketAttachment(TimestampMixin, Base):
    __tablename__ = "ticket_attachments"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    ticket_id: Mapped[str] = mapped_column(ForeignKey("support_tickets.id", ondelete="CASCADE"), index=True, nullable=False)
    uploaded_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    media_type: Mapped[str] = mapped_column(String(120), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[bytes] = deferred(mapped_column(LargeBinary, nullable=False))


class ChatConversation(TimestampMixin, Base):
    __tablename__ = "chat_conversations"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), default="Cuộc trò chuyện mới", nullable=False)
    messages: Mapped[list["ChatMessage"]] = relationship(back_populates="conversation", cascade="all, delete-orphan", order_by="ChatMessage.created_at")


class ChatMessage(TimestampMixin, Base):
    __tablename__ = "chat_messages"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    conversation_id: Mapped[str] = mapped_column(ForeignKey("chat_conversations.id", ondelete="CASCADE"), index=True, nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    sources: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    conversation: Mapped[ChatConversation] = relationship(back_populates="messages")


class KnowledgeDocument(TimestampMixin, Base):
    __tablename__ = "knowledge_documents"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    media_type: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="processing", index=True, nullable=False)
    uploaded_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    chunks: Mapped[list["KnowledgeChunk"]] = relationship(back_populates="document", cascade="all, delete-orphan")


class KnowledgeChunk(TimestampMixin, Base):
    __tablename__ = "knowledge_chunks"
    __table_args__ = (
        Index("ix_chunks_document", "document_id"),
        Index("ix_chunks_embedding_cosine", "embedding", postgresql_using="hnsw",
              postgresql_ops={"embedding": "vector_cosine_ops"},
              postgresql_with={"m": 16, "ef_construction": 64}),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    document_id: Mapped[str] = mapped_column(ForeignKey("knowledge_documents.id", ondelete="CASCADE"), nullable=False)
    ordinal: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1536).with_variant(JSON(), "sqlite"), nullable=True)
    document: Mapped[KnowledgeDocument] = relationship(back_populates="chunks")


class FAQ(TimestampMixin, Base):
    __tablename__ = "faqs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    question: Mapped[str] = mapped_column(String(500), nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(80), default="Chung", nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
