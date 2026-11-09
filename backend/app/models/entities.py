from datetime import date, datetime, timezone, time
from uuid import uuid4

from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Index, Integer, JSON, LargeBinary, String, Text, Float, Time, UniqueConstraint
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
    admission_method: Mapped[str] = mapped_column(String(100), default="Học bạ", nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="Mới tiếp nhận", index=True, nullable=False)
    review_note: Mapped[str] = mapped_column(Text, default="", nullable=False)
    details: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    student_id: Mapped[str | None] = mapped_column(ForeignKey("students.id"), nullable=True, unique=True)
    major: Mapped[Major] = relationship()
    preferences: Mapped[list["ApplicantPreference"]] = relationship(cascade="all, delete-orphan", order_by="ApplicantPreference.preference_order")
    documents: Mapped[list["ApplicantDocument"]] = relationship(cascade="all, delete-orphan", order_by="ApplicantDocument.created_at")


class ApplicantPreference(TimestampMixin, Base):
    __tablename__ = "applicant_preferences"
    __table_args__ = (UniqueConstraint("applicant_id", "preference_order", name="uq_applicant_preference_order"),
                      UniqueConstraint("applicant_id", "major_id", name="uq_applicant_preference_major"))
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    applicant_id: Mapped[str] = mapped_column(ForeignKey("applicants.id", ondelete="CASCADE"), index=True, nullable=False)
    major_id: Mapped[str] = mapped_column(ForeignKey("majors.id"), index=True, nullable=False)
    preference_order: Mapped[int] = mapped_column(Integer, nullable=False)
    program_name: Mapped[str] = mapped_column(String(180), default="", nullable=False)
    admission_method: Mapped[str] = mapped_column(String(100), default="", nullable=False)
    major: Mapped[Major] = relationship()


class ApplicantDocument(TimestampMixin, Base):
    __tablename__ = "applicant_documents"
    __table_args__ = (Index("ix_applicant_documents_applicant_status", "applicant_id", "status"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    applicant_id: Mapped[str] = mapped_column(ForeignKey("applicants.id", ondelete="CASCADE"), index=True, nullable=False)
    uploaded_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    document_type: Mapped[str] = mapped_column(String(100), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    media_type: Mapped[str] = mapped_column(String(120), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[bytes] = deferred(mapped_column(LargeBinary, nullable=False))
    status: Mapped[str] = mapped_column(String(30), default="Chờ kiểm tra", index=True, nullable=False)
    review_note: Mapped[str] = mapped_column(String(1000), default="", nullable=False)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewed_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)


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


class Semester(TimestampMixin, Base):
    __tablename__ = "semesters"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    code: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    academic_year: Mapped[str] = mapped_column(String(20), nullable=False)
    starts_on: Mapped[date] = mapped_column(Date, nullable=False)
    ends_on: Mapped[date] = mapped_column(Date, nullable=False)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class Course(TimestampMixin, Base):
    __tablename__ = "courses"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    code: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    credits: Mapped[int] = mapped_column(Integer, nullable=False)
    major_id: Mapped[str | None] = mapped_column(ForeignKey("majors.id"), index=True, nullable=True)


class CourseOffering(TimestampMixin, Base):
    __tablename__ = "course_offerings"
    __table_args__ = (UniqueConstraint("course_id", "semester_id", "section", name="uq_offering_course_semester_section"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    course_id: Mapped[str] = mapped_column(ForeignKey("courses.id"), index=True, nullable=False)
    semester_id: Mapped[str] = mapped_column(ForeignKey("semesters.id"), index=True, nullable=False)
    lecturer_id: Mapped[str | None] = mapped_column(ForeignKey("personnel.id"), index=True, nullable=True)
    section: Mapped[str] = mapped_column(String(20), nullable=False)
    room: Mapped[str] = mapped_column(String(80), default="", nullable=False)
    delivery_mode: Mapped[str] = mapped_column(String(60), default="Trực tiếp", nullable=False)
    note: Mapped[str] = mapped_column(String(500), default="", nullable=False)
    weekday: Mapped[int] = mapped_column(Integer, nullable=False)
    starts_at: Mapped[time] = mapped_column(Time, nullable=False)
    ends_at: Mapped[time] = mapped_column(Time, nullable=False)
    course: Mapped[Course] = relationship()
    semester: Mapped[Semester] = relationship()
    lecturer: Mapped["Personnel | None"] = relationship()


class CourseEnrollment(TimestampMixin, Base):
    __tablename__ = "course_enrollments"
    __table_args__ = (UniqueConstraint("student_id", "offering_id", name="uq_enrollment_student_offering"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    student_id: Mapped[str] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), index=True, nullable=False)
    offering_id: Mapped[str] = mapped_column(ForeignKey("course_offerings.id", ondelete="CASCADE"), index=True, nullable=False)
    attendance_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    midterm_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    final_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    letter_grade: Mapped[str] = mapped_column(String(3), default="", nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="Đang học", nullable=False)
    student: Mapped[Student] = relationship()
    offering: Mapped[CourseOffering] = relationship()


class Exam(TimestampMixin, Base):
    __tablename__ = "exams"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    offering_id: Mapped[str] = mapped_column(ForeignKey("course_offerings.id", ondelete="CASCADE"), index=True, nullable=False)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    room: Mapped[str] = mapped_column(String(80), nullable=False)
    exam_type: Mapped[str] = mapped_column(String(60), default="Trực tiếp", nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    note: Mapped[str] = mapped_column(String(500), default="", nullable=False)
    offering: Mapped[CourseOffering] = relationship()


class ConductRecord(TimestampMixin, Base):
    __tablename__ = "conduct_records"
    __table_args__ = (UniqueConstraint("student_id", "semester_id", name="uq_conduct_student_semester"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    student_id: Mapped[str] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), index=True, nullable=False)
    semester_id: Mapped[str] = mapped_column(ForeignKey("semesters.id"), index=True, nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    rating: Mapped[str] = mapped_column(String(40), nullable=False)
    comment: Mapped[str] = mapped_column(Text, default="", nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="Đã công bố", nullable=False)
    evaluated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    semester: Mapped[Semester] = relationship()


class StudentCharge(TimestampMixin, Base):
    __tablename__ = "student_charges"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    student_id: Mapped[str] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), index=True, nullable=False)
    semester_id: Mapped[str] = mapped_column(ForeignKey("semesters.id"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    amount_due: Mapped[int] = mapped_column(Integer, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="Chưa thanh toán", nullable=False)
    semester: Mapped[Semester] = relationship()
    transactions: Mapped[list["PaymentTransaction"]] = relationship(back_populates="charge", cascade="all, delete-orphan")


class PaymentTransaction(TimestampMixin, Base):
    __tablename__ = "payment_transactions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    charge_id: Mapped[str] = mapped_column(ForeignKey("student_charges.id", ondelete="CASCADE"), index=True, nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    paid_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    reference: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    note: Mapped[str] = mapped_column(String(300), default="", nullable=False)
    charge: Mapped[StudentCharge] = relationship(back_populates="transactions")


class Assignment(TimestampMixin, Base):
    __tablename__ = "assignments"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    offering_id: Mapped[str] = mapped_column(ForeignKey("course_offerings.id", ondelete="CASCADE"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    offering: Mapped[CourseOffering] = relationship()
    submissions: Mapped[list["AssignmentSubmission"]] = relationship(back_populates="assignment", cascade="all, delete-orphan")


class AssignmentSubmission(TimestampMixin, Base):
    __tablename__ = "assignment_submissions"
    __table_args__ = (UniqueConstraint("assignment_id", "student_id", name="uq_submission_assignment_student"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    assignment_id: Mapped[str] = mapped_column(ForeignKey("assignments.id", ondelete="CASCADE"), index=True, nullable=False)
    student_id: Mapped[str] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), index=True, nullable=False)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="Chưa làm", nullable=False)
    content: Mapped[str] = mapped_column(Text, default="", nullable=False)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    assignment: Mapped[Assignment] = relationship(back_populates="submissions")


class NewsArticle(TimestampMixin, Base):
    __tablename__ = "news_articles"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    slug: Mapped[str] = mapped_column(String(220), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    category: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    summary: Mapped[str] = mapped_column(String(600), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    image_url: Mapped[str] = mapped_column(String(500), default="", nullable=False)
    source_url: Mapped[str] = mapped_column(String(500), default="", nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="draft", index=True, nullable=False)


class UniversityEvent(TimestampMixin, Base):
    __tablename__ = "university_events"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(String(80), nullable=False)
    summary: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(180), nullable=False)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_all_day: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    source_url: Mapped[str] = mapped_column(String(500), default="", nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="published", nullable=False)


class AttendanceSession(TimestampMixin, Base):
    __tablename__ = "attendance_sessions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    offering_id: Mapped[str] = mapped_column(ForeignKey("course_offerings.id", ondelete="CASCADE"), index=True, nullable=False)
    opened_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="open", index=True, nullable=False)


class AttendanceRecord(TimestampMixin, Base):
    __tablename__ = "attendance_records"
    __table_args__ = (UniqueConstraint("session_id", "student_id", name="uq_attendance_session_student"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    session_id: Mapped[str] = mapped_column(ForeignKey("attendance_sessions.id", ondelete="CASCADE"), index=True, nullable=False)
    student_id: Mapped[str] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="absent", nullable=False)
    marked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    marked_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    session: Mapped[AttendanceSession] = relationship()
    student: Mapped[Student] = relationship()


class AttendanceEvidence(TimestampMixin, Base):
    __tablename__ = "attendance_evidence"
    __table_args__ = (UniqueConstraint("session_id", "student_id", name="uq_attendance_evidence_session_student"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    session_id: Mapped[str] = mapped_column(ForeignKey("attendance_sessions.id", ondelete="CASCADE"), index=True, nullable=False)
    student_id: Mapped[str] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), index=True, nullable=False)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    media_type: Mapped[str] = mapped_column(String(80), nullable=False)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)


class AttendanceMakeupRequest(TimestampMixin, Base):
    __tablename__ = "attendance_makeup_requests"
    __table_args__ = (UniqueConstraint("record_id", name="uq_attendance_makeup_record"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    record_id: Mapped[str] = mapped_column(ForeignKey("attendance_records.id", ondelete="CASCADE"), index=True, nullable=False)
    evidence_id: Mapped[str | None] = mapped_column(ForeignKey("attendance_evidence.id"), nullable=True)
    request_reason: Mapped[str] = mapped_column(Text, default="", nullable=False)
    request_photo_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    request_photo_media_type: Mapped[str | None] = mapped_column(String(80), nullable=True)
    request_photo_captured_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    request_photo_received_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True, nullable=False)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewed_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    review_reason: Mapped[str] = mapped_column(String(1000), default="", nullable=False)
    evidence: Mapped[AttendanceEvidence | None] = relationship()


class AttendanceAuditLog(TimestampMixin, Base):
    __tablename__ = "attendance_audit_logs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    session_id: Mapped[str] = mapped_column(ForeignKey("attendance_sessions.id", ondelete="CASCADE"), index=True, nullable=False)
    record_id: Mapped[str | None] = mapped_column(ForeignKey("attendance_records.id", ondelete="SET NULL"), index=True, nullable=True)
    actor_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    action: Mapped[str] = mapped_column(String(40), nullable=False)
    details: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class CourseGradeAudit(TimestampMixin, Base):
    __tablename__ = "course_grade_audit"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    enrollment_id: Mapped[str] = mapped_column(ForeignKey("course_enrollments.id", ondelete="CASCADE"), index=True, nullable=False)
    actor_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    previous_values: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    new_values: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class Personnel(TimestampMixin, Base):
    """Shared employee record for academic staff and university employees."""
    __tablename__ = "personnel"
    __table_args__ = (
        Index("ix_personnel_type_status", "kind", "work_status"),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), unique=True, nullable=True)
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
    user: Mapped[User | None] = relationship()


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


class GuestChatSession(TimestampMixin, Base):
    __tablename__ = "guest_chat_sessions"
    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    messages: Mapped[list["GuestChatMessage"]] = relationship(back_populates="session", cascade="all, delete-orphan", order_by="GuestChatMessage.created_at")


class GuestChatMessage(TimestampMixin, Base):
    __tablename__ = "guest_chat_messages"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    session_hash: Mapped[str] = mapped_column(ForeignKey("guest_chat_sessions.token_hash", ondelete="CASCADE"), index=True, nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    sources: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    session: Mapped[GuestChatSession] = relationship(back_populates="messages")


class KnowledgeDocument(TimestampMixin, Base):
    __tablename__ = "knowledge_documents"
    __table_args__ = (Index("uq_knowledge_documents_source_path", "source_path", unique=True),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    media_type: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="processing", index=True, nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    uploaded_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    source_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    source_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
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
