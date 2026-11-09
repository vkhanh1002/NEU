from datetime import date, datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    email: str
    full_name: str
    role: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserPublic


class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    password: str

    @field_validator("email")
    @classmethod
    def normalize_login_email(cls, value: str) -> str:
        email = value.strip().lower()
        local, separator, domain = email.partition("@")
        if not separator or not local or not domain or "@" in domain or "." not in domain or any(char.isspace() for char in email):
            raise ValueError("Email chưa đúng định dạng.")
        return email


class MajorPublic(BaseModel):
    id: str
    code: str
    name: str
    description: str
    faculty_name: str
    duration_years: int
    tuition_per_year_vnd: int
    admission_quota: int
    admission_status: str
    is_demo: bool


class ApplicantCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=180)
    password: str | None = Field(default=None, min_length=8, max_length=128)
    phone: str = Field(default="", max_length=40)
    date_of_birth: date | None = None
    address: str = Field(default="", max_length=500)
    desired_major_id: str
    admission_method: str = Field(default="Học bạ", min_length=1, max_length=100)
    details: dict[str, object] = Field(default_factory=dict, max_length=80)
    preferences: list[str] = Field(default_factory=list, max_length=10)
    confirmed: bool = False

    @field_validator("details")
    @classmethod
    def bound_details(cls, value: dict[str, object]) -> dict[str, object]:
        if len(value) > 80:
            raise ValueError("Hồ sơ có quá nhiều trường thông tin.")
        total_length = 0
        for key, item in value.items():
            if not isinstance(key, str) or len(key) > 120:
                raise ValueError("Tên trường thông tin không hợp lệ.")
            if isinstance(item, str):
                total_length += len(item)
                if len(item) > 2000:
                    raise ValueError("Mỗi trường thông tin tối đa 2.000 ký tự.")
            elif item is not None and not isinstance(item, (bool, int, float)):
                raise ValueError("Giá trị chi tiết hồ sơ không hợp lệ.")
        if total_length > 12000:
            raise ValueError("Tổng nội dung chi tiết hồ sơ quá dài.")
        return value

    @field_validator("preferences")
    @classmethod
    def unique_preferences(cls, value: list[str]) -> list[str]:
        if len(value) != len(set(value)):
            raise ValueError("Nguyện vọng không được trùng ngành.")
        return value


class ApplicantPreferencePublic(BaseModel):
    major_id: str
    major_name: str
    program_name: str
    preference_order: int
    admission_method: str


class ApplicantStatusUpdate(BaseModel):
    status: str
    note: str | None = Field(default=None, max_length=1000)


class ApplicantPublic(BaseModel):
    id: str
    email: str
    full_name: str
    phone: str
    desired_major_id: str
    major_name: str
    admission_method: str
    status: str
    review_note: str
    details: dict[str, object] = Field(default_factory=dict)
    preferences: list[ApplicantPreferencePublic] = Field(default_factory=list)
    created_at: datetime
    student_id: str | None


class StudentPublic(BaseModel):
    id: str
    student_number: str
    full_name: str
    email: str
    phone: str
    date_of_birth: date | None
    gender: str
    address: str
    emergency_contact: dict
    major_id: str
    major_name: str
    cohort: str
    class_name: str
    study_status: str
    enrollment_date: date | None
    is_demo: bool


class StudentProfileUpdate(BaseModel):
    phone: str | None = Field(default=None, max_length=40)
    address: str | None = Field(default=None, max_length=500)
    gender: str | None = Field(default=None, max_length=30)
    emergency_contact: dict | None = None


class PersonnelCreate(BaseModel):
    code: str = Field(min_length=2, max_length=30)
    kind: Literal["lecturer", "employee"]
    full_name: str = Field(min_length=2, max_length=180)
    email: EmailStr
    phone: str = ""
    date_of_birth: date | None = None
    gender: str = "Chưa cập nhật"
    address: str = ""
    avatar_url: str = ""
    education_level: str = ""
    academic_rank: str = ""
    specialty: str = ""
    faculty_id: str | None = None
    department: str = ""
    position: str = ""
    start_date: date | None = None
    work_status: str = "Đang công tác"
    notes: str = ""


class PersonnelUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=180)
    email: EmailStr | None = None
    phone: str | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    address: str | None = None
    avatar_url: str | None = None
    education_level: str | None = None
    academic_rank: str | None = None
    specialty: str | None = None
    faculty_id: str | None = None
    department: str | None = None
    position: str | None = None
    start_date: date | None = None
    work_status: str | None = None
    notes: str | None = None


class PersonnelPublic(BaseModel):
    id: str
    code: str
    kind: str
    full_name: str
    email: str
    phone: str
    date_of_birth: date | None
    gender: str
    address: str
    avatar_url: str
    education_level: str
    academic_rank: str
    specialty: str
    faculty_id: str | None
    faculty_name: str | None
    department: str
    position: str
    start_date: date | None
    work_status: str
    notes: str
    is_demo: bool


class TicketCreate(BaseModel):
    category: str
    subject: str = Field(min_length=4, max_length=200)
    description: str = Field(min_length=8, max_length=10000)
    priority: str = "Bình thường"


class TicketStatusUpdate(BaseModel):
    status: str


class TicketAssign(BaseModel):
    assignee_id: str | None


class TicketRating(BaseModel):
    rating: int = Field(ge=1, le=5)
    feedback: str = Field(default="", max_length=1000)


class TicketReply(BaseModel):
    body: str = Field(min_length=1, max_length=10000)


class TicketMessagePublic(BaseModel):
    id: str
    author_id: str
    body: str
    created_at: datetime


class TicketAttachmentPublic(BaseModel):
    id: str
    filename: str
    media_type: str
    size_bytes: int
    uploaded_at: datetime


class TicketPublic(BaseModel):
    id: str
    code: str
    owner_id: str
    owner_name: str
    category: str
    subject: str
    description: str
    priority: str
    status: str
    assignee_id: str | None
    satisfaction_rating: int | None
    satisfaction_feedback: str | None
    created_at: datetime
    messages: list[TicketMessagePublic]
    attachments: list[TicketAttachmentPublic] = []


class ConversationCreate(BaseModel):
    title: str = "Cuộc trò chuyện mới"


class ConversationRename(BaseModel):
    title: str = Field(min_length=1, max_length=180)


class ChatAsk(BaseModel):
    message: str = Field(min_length=1, max_length=8000)


class SourcePublic(BaseModel):
    title: str
    excerpt: str
    source_type: str


class ChatMessagePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    role: str
    content: str
    sources: list[dict]
    created_at: datetime


class ConversationPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    title: str
    updated_at: datetime
    messages: list[ChatMessagePublic] = []


class FAQPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    question: str
    answer: str
    category: str


class FAQCreate(BaseModel):
    question: str = Field(min_length=6, max_length=500)
    answer: str = Field(min_length=8)
    category: str = "Chung"


class FAQAdminPublic(FAQPublic):
    is_published: bool


class AIStatusPublic(BaseModel):
    provider: str
    model: str
    configured: bool
    fallback_provider: str | None
    fallback_configured: bool
    connection_status: str
    llm_configured: bool
    llm_model: str
    embedding_model: str | None
    embedding_provider: str
    retrieval_mode: str


class NotificationPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    title: str
    message: str
    href: str
    read_at: datetime | None
    created_at: datetime


class DocumentPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    filename: str
    media_type: str
    status: str
    is_public: bool = False
    error: str | None
    created_at: datetime


class DocumentVisibilityUpdate(BaseModel):
    is_public: bool


class DashboardPublic(BaseModel):
    year: int
    students: int
    applications: int
    majors: int
    pending_tickets: int
    admissions_by_month: list[dict]
    students_by_major: list[dict]
    recent_activity: list[dict]
