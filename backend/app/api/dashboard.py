from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import extract, func, select
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.database import get_db
from app.models import Applicant, Major, Student, SupportTicket, User

router = APIRouter(tags=["Dashboard"])


@router.get("/dashboard")
def dashboard(user: User = Depends(require_roles("super_admin", "admission_staff", "lecturer", "support_staff", "hr_staff", "academic_staff")), db: Session = Depends(get_db)):
    students = db.scalar(select(func.count(Student.id))) or 0
    applications = db.scalar(select(func.count(Applicant.id))) or 0
    majors = db.scalar(select(func.count(Major.id))) or 0
    pending = db.scalar(select(func.count(SupportTicket.id)).where(SupportTicket.status.in_(["Mới tiếp nhận", "Đang xử lý", "Chờ bổ sung thông tin"]))) or 0
    now = datetime.now(timezone.utc)
    month_counts = db.execute(
        select(extract("month", Applicant.created_at), func.count(Applicant.id))
        .where(extract("year", Applicant.created_at) == now.year)
        .group_by(extract("month", Applicant.created_at))
    ).all()
    by_month = {int(month): count for month, count in month_counts}
    admissions = [{"month": f"T{month}", "applications": by_month.get(month, 0)} for month in range(1, 13)]
    by_major = db.execute(
        select(Major.name, func.count(Student.id)).outerjoin(Student, Student.major_id == Major.id).group_by(Major.id).order_by(func.count(Student.id).desc()).limit(6)
    ).all()
    major_distribution = [{"name": name, "students": count} for name, count in by_major]
    activity = []
    if user.role in {"super_admin", "admission_staff"}:
        for applicant in db.scalars(select(Applicant).order_by(Applicant.created_at.desc()).limit(3)).all():
            activity.append({"title": f"Hồ sơ mới: {applicant.full_name}", "detail": applicant.status, "at": applicant.created_at.isoformat(), "kind": "admission"})
    if user.role in {"super_admin", "support_staff"}:
        for ticket in db.scalars(select(SupportTicket).order_by(SupportTicket.created_at.desc()).limit(3)).all():
            activity.append({"title": f"Yêu cầu {ticket.code}: {ticket.subject}", "detail": ticket.status, "at": ticket.created_at.isoformat(), "kind": "support"})
    activity.sort(key=lambda item: item["at"], reverse=True)
    return {"year": now.year, "students": students, "applications": applications, "majors": majors,
            "pending_tickets": pending if user.role in {"super_admin", "support_staff"} else 0,
            "admissions_by_month": admissions, "students_by_major": major_distribution,
            "recent_activity": activity[:5]}
