from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Applicant, Major, Student, SupportTicket

router = APIRouter(tags=["Dashboard"])


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db)):
    students = db.scalar(select(func.count(Student.id))) or 0
    applications = db.scalar(select(func.count(Applicant.id))) or 0
    majors = db.scalar(select(func.count(Major.id))) or 0
    pending = db.scalar(select(func.count(SupportTicket.id)).where(SupportTicket.status.in_(["Mới tiếp nhận", "Đang xử lý", "Chờ bổ sung thông tin"]))) or 0
    # Demonstration analytics are labeled here and in the API response.
    admissions = [
        {"month": month, "applications": value}
        for month, value in zip(["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9", "T10", "T11", "T12"], [42, 58, 72, 65, 91, 110, 138, 124, 97, 83, 54, 31])
    ]
    by_major = db.execute(
        select(Major.name, func.count(Student.id)).outerjoin(Student, Student.major_id == Major.id).group_by(Major.id).order_by(func.count(Student.id).desc()).limit(6)
    ).all()
    major_distribution = [{"name": name, "students": count} for name, count in by_major]
    activity = []
    for applicant in db.scalars(select(Applicant).order_by(Applicant.created_at.desc()).limit(3)).all():
        activity.append({"title": f"Hồ sơ mới: {applicant.full_name}", "detail": applicant.status, "at": applicant.created_at.isoformat(), "kind": "admission"})
    for ticket in db.scalars(select(SupportTicket).order_by(SupportTicket.created_at.desc()).limit(3)).all():
        activity.append({"title": f"Yêu cầu {ticket.code}: {ticket.subject}", "detail": ticket.status, "at": ticket.created_at.isoformat(), "kind": "support"})
    activity.sort(key=lambda item: item["at"], reverse=True)
    return {"students": students, "applications": applications, "majors": majors, "pending_tickets": pending,
            "admissions_by_month": admissions, "students_by_major": major_distribution,
            "recent_activity": activity[:5], "demo_data": True}
