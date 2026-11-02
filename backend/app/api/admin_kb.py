import json
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import current_user, require_roles
from app.core.database import get_db
from app.models import (
    AdmissionProgram, AdmissionScore, ChatFeedback, Department,
    FAQ, FaqItem, KbAuditLog, KnowledgeChunk, KnowledgeDocument, TuitionFee,
    UnansweredQuestion, User
)
from app.schemas_kb import (
    AdmissionProgramPublic, AdmissionScorePublic, DepartmentPublic,
    FaqItemPublic, TuitionFeePublic, UnansweredQuestionPublic
)

logger = logging.getLogger(__name__)
admin_kb_router = APIRouter(prefix="/admin/kb", tags=["Admin Knowledge Base Management"])
ADMIN_ROLES = ("super_admin", "admin", "editor")


def _log_kb_action(db: Session, user_id: str, action: str, entity_type: str, entity_id: str, details: dict):
    audit = KbAuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details
    )
    db.add(audit)
    db.commit()


@admin_kb_router.get("/unanswered", response_model=list[UnansweredQuestionPublic])
def list_unanswered_questions(
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*ADMIN_ROLES))
):
    """Danh sách các câu hỏi người dùng đặt mà AI chưa có thông tin chính thức để trả lời."""
    return db.scalars(
        select(UnansweredQuestion)
        .order_by(UnansweredQuestion.resolved.asc(), UnansweredQuestion.created_at.desc())
        .limit(100)
    ).all()


@admin_kb_router.patch("/unanswered/{question_id}/resolve")
def resolve_unanswered_question(
    question_id: str,
    note: str = Query(default=""),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*ADMIN_ROLES))
):
    """Đánh dấu đã bổ sung tri thức cho câu hỏi chưa giải đáp."""
    q = db.get(UnansweredQuestion, question_id)
    if not q:
        raise HTTPException(status_code=404, detail="Không tìm thấy câu hỏi.")
    q.resolved = True
    q.resolved_by = user.id
    q.resolution_note = note
    db.commit()
    _log_kb_action(db, user.id, "resolve", "unanswered_question", question_id, {"note": note})
    return {"status": "ok", "message": "Đã đánh dấu giải quyết."}


@admin_kb_router.get("/analytics")
def get_chat_analytics(
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*ADMIN_ROLES))
):
    """Thống kê chất lượng phản hồi: đánh giá tích cực/tiêu cực, số câu hỏi chưa có tài liệu."""
    total_feedbacks = db.scalar(select(func.count(ChatFeedback.id))) or 0
    positive_feedbacks = db.scalar(select(func.count(ChatFeedback.id)).where(ChatFeedback.is_positive.is_(True))) or 0
    unanswered_count = db.scalar(select(func.count(UnansweredQuestion.id)).where(UnansweredQuestion.resolved.is_(False))) or 0
    satisfaction_rate = round((positive_feedbacks / total_feedbacks * 100), 1) if total_feedbacks > 0 else 100.0

    return {
        "total_feedbacks": total_feedbacks,
        "positive_feedbacks": positive_feedbacks,
        "negative_feedbacks": total_feedbacks - positive_feedbacks,
        "satisfaction_rate_percent": satisfaction_rate,
        "unanswered_questions_pending": unanswered_count,
    }


@admin_kb_router.patch("/documents/{document_id}/archive")
def archive_kb_document(
    document_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*ADMIN_ROLES))
):
    """Lưu trữ (archive) tài liệu cũ để AI không trả lời nhầm phiên bản cũ."""
    doc = db.get(KnowledgeDocument, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài liệu.")
    doc.status = "archived"
    db.commit()
    _log_kb_action(db, user.id, "archive", "document", document_id, {"filename": doc.filename})
    return {"status": "ok", "message": f"Tài liệu {doc.filename} đã được lưu trữ (archived)."}


@admin_kb_router.patch("/documents/{document_id}/publish")
def publish_kb_document(
    document_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*ADMIN_ROLES))
):
    """Công bố (publish) tài liệu mới vào kho tri thức phục vụ tra cứu."""
    doc = db.get(KnowledgeDocument, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài liệu.")
    doc.status = "published"
    db.commit()
    _log_kb_action(db, user.id, "publish", "document", document_id, {"filename": doc.filename})
    return {"status": "ok", "message": f"Tài liệu {doc.filename} đã được công bố chính thức."}
