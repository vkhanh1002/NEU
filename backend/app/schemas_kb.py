from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field


class GuestChatAsk(BaseModel):
    message: str = Field(min_length=1, max_length=1500)


class ChatFeedbackCreate(BaseModel):
    is_positive: bool
    reason: str = ""
    comment: str = ""


class DepartmentPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    code: str
    description: str
    email: str
    phone: str
    location: str
    office_hours: str


class AdmissionProgramPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    major_code: str
    name: str
    program_type: str
    quota: int
    methods: list
    subject_groups: str
    year: int
    note: str


class AdmissionScorePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    program_code: str
    program_name: str
    year: int
    method: str
    score: float
    scale: int
    note: str


class TuitionFeePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    program_code: str
    program_name: str
    cohort: str
    academic_year: str
    per_credit_vnd: int
    per_year_vnd: int
    note: str


class FaqItemPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    question: str
    answer: str
    category: str
    audience: str
    status: str


class UnansweredQuestionPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    question: str
    user_type: str
    resolved: bool
    created_at: datetime
