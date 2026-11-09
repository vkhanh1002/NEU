from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import current_user
from app.core.database import get_db
from app.models import (Assignment, AssignmentSubmission, ConductRecord, CourseEnrollment, CourseOffering,
                        Exam, PaymentTransaction, Semester, Student, StudentCharge, User)
from app.services.schedule import serialize_schedule

router = APIRouter(prefix="/student", tags=["Student academic services"])


def current_student(user: User, db: Session) -> Student:
    if user.role != "student":
        raise HTTPException(status_code=403, detail="Chức năng chỉ dành cho tài khoản sinh viên.")
    student = db.scalar(select(Student).where(Student.user_id == user.id).options(joinedload(Student.major)))
    if not student:
        raise HTTPException(status_code=404, detail="Tài khoản chưa được liên kết với hồ sơ sinh viên.")
    return student


def _semesters(db: Session):
    return db.scalars(select(Semester).order_by(Semester.starts_on.desc())).all()


def _as_utc(value: datetime) -> datetime:
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


def _offering_data(offering: CourseOffering) -> dict:
    return {**serialize_schedule(offering), "credits": offering.course.credits}


@router.get("/overview")
def learning_overview(user: User = Depends(current_user), db: Session = Depends(get_db)):
    student = current_student(user, db)
    semester = db.scalar(select(Semester).where(Semester.is_current.is_(True)).order_by(Semester.starts_on.desc()))
    enrollments = db.scalars(
        select(CourseEnrollment).join(CourseOffering).join(Semester)
        .where(CourseEnrollment.student_id == student.id)
        .options(joinedload(CourseEnrollment.offering).joinedload(CourseOffering.course),
                 joinedload(CourseEnrollment.offering).joinedload(CourseOffering.semester))
    ).all()
    completed = [row for row in enrollments if row.status == "Hoàn thành"]
    passed = [row for row in completed if row.total_score is not None and row.total_score >= 5]
    credits_earned = sum(row.offering.course.credits for row in passed)
    grade_points = {"A": 4.0, "A-": 3.7, "B+": 3.3, "B": 3.0, "B-": 2.7, "C+": 2.3,
                    "C": 2.0, "C-": 1.7, "D+": 1.3, "D": 1.0, "F": 0.0}
    graded = [row for row in completed if row.letter_grade in grade_points]
    gpa = round(sum(grade_points[row.letter_grade] * row.offering.course.credits for row in graded) /
                sum(row.offering.course.credits for row in graded), 2) if graded else None
    current_rows = [row for row in enrollments if semester and row.offering.semester_id == semester.id and row.status == "Đang học"]
    conduct = db.scalar(select(ConductRecord).join(Semester).where(ConductRecord.student_id == student.id)
                        .order_by(Semester.starts_on.desc()))
    upcoming_exams = db.scalars(select(Exam).join(CourseOffering).join(CourseEnrollment)
                                .where(CourseEnrollment.student_id == student.id, Exam.starts_at >= datetime.now(timezone.utc))
                                .options(joinedload(Exam.offering).joinedload(CourseOffering.course))
                                .order_by(Exam.starts_at).limit(5)).all()
    due_rows = db.scalars(select(AssignmentSubmission).join(Assignment).join(CourseOffering)
                          .where(AssignmentSubmission.student_id == student.id,
                                 AssignmentSubmission.status.in_(["Chưa làm", "Đang thực hiện"]))
                          .options(joinedload(AssignmentSubmission.assignment).joinedload(Assignment.offering).joinedload(CourseOffering.course))
                          .order_by(Assignment.deadline).limit(5)).all()
    charges = db.scalars(select(StudentCharge).where(StudentCharge.student_id == student.id)
                         .options(joinedload(StudentCharge.transactions), joinedload(StudentCharge.semester))
                         .order_by(StudentCharge.due_date)).unique().all()
    outstanding = sum(max(0, row.amount_due - sum(tx.amount for tx in row.transactions)) for row in charges)
    return {
        "student": {"student_number": student.student_number, "full_name": student.full_name, "email": student.email,
                    "major_name": student.major.name, "class_name": student.class_name, "cohort": student.cohort,
                    "study_status": student.study_status, "enrollment_date": student.enrollment_date},
        "current_semester": {"code": semester.code, "name": semester.name, "academic_year": semester.academic_year} if semester else None,
        "credits_earned": credits_earned, "credits_required": 130, "gpa": gpa,
        "conduct": {"score": conduct.score, "rating": conduct.rating, "semester": conduct.semester.name} if conduct else None,
        "current_courses": [_offering_data(row.offering) for row in current_rows],
        "upcoming_exams": [{**_offering_data(row.offering), "starts_at_datetime": row.starts_at,
                            "room": row.room, "exam_type": row.exam_type, "duration_minutes": row.duration_minutes,
                            "note": row.note} for row in upcoming_exams],
        "upcoming_assignments": [{"id": row.assignment.id, "title": row.assignment.title,
                                  "course_name": row.assignment.offering.course.name,
                                  "deadline": row.assignment.deadline, "status": row.status} for row in due_rows],
        "outstanding_amount": outstanding,
        "failed_courses": [{"course_code": row.offering.course.code, "course_name": row.offering.course.name,
                            "semester": row.offering.semester.name, "total_score": row.total_score}
                           for row in enrollments if row.status == "Hoàn thành" and row.total_score is not None and row.total_score < 5],
    }


@router.get("/semesters")
def list_student_semesters(user: User = Depends(current_user), db: Session = Depends(get_db)):
    current_student(user, db)
    return [{"id": row.id, "code": row.code, "name": row.name, "academic_year": row.academic_year,
             "starts_on": row.starts_on, "ends_on": row.ends_on, "is_current": row.is_current} for row in _semesters(db)]


@router.get("/schedule")
def student_schedule(semester_id: str | None = None, academic_year: str | None = None,
                     course_code: str | None = None, section: str | None = None,
                     user: User = Depends(current_user), db: Session = Depends(get_db)):
    student = current_student(user, db)
    query = (select(CourseEnrollment).join(CourseOffering).where(CourseEnrollment.student_id == student.id)
             .options(joinedload(CourseEnrollment.offering).joinedload(CourseOffering.course),
                      joinedload(CourseEnrollment.offering).joinedload(CourseOffering.semester),
                      joinedload(CourseEnrollment.offering).joinedload(CourseOffering.lecturer)))
    if semester_id and semester_id != "all":
        query = query.where(CourseOffering.semester_id == semester_id)
    elif semester_id != "all" and db.scalar(select(Semester.id).where(Semester.is_current.is_(True))):
        query = query.where(CourseOffering.semester_id == select(Semester.id).where(Semester.is_current.is_(True)).limit(1).scalar_subquery())
    if academic_year:
        query = query.join(Semester).where(Semester.academic_year == academic_year)
    if course_code:
        from app.models import Course
        query = query.join(Course).where(Course.code == course_code)
    if section:
        query = query.where(CourseOffering.section == section)
    rows = db.scalars(query.order_by(CourseOffering.weekday, CourseOffering.starts_at)).all()
    return {"items": [_offering_data(row.offering) for row in rows], "count": len(rows)}


@router.get("/exams")
def student_exams(semester_id: str | None = None, user: User = Depends(current_user), db: Session = Depends(get_db)):
    student = current_student(user, db)
    query = (select(Exam).join(CourseOffering).join(CourseEnrollment)
             .where(CourseEnrollment.student_id == student.id)
             .options(joinedload(Exam.offering).joinedload(CourseOffering.course),
                      joinedload(Exam.offering).joinedload(CourseOffering.semester)))
    if semester_id and semester_id != "all":
        query = query.where(CourseOffering.semester_id == semester_id)
    rows = db.scalars(query.order_by(Exam.starts_at)).all()
    now = datetime.now(timezone.utc)
    return {"upcoming": [{**_offering_data(row.offering), "exam_id": row.id, "starts_at": row.starts_at,
                          "room": row.room, "exam_type": row.exam_type, "duration_minutes": row.duration_minutes,
                          "note": row.note} for row in rows if _as_utc(row.starts_at) >= now],
            "past": [{**_offering_data(row.offering), "exam_id": row.id, "starts_at": row.starts_at,
                      "room": row.room, "exam_type": row.exam_type, "duration_minutes": row.duration_minutes,
                      "note": row.note} for row in rows if _as_utc(row.starts_at) < now]}


@router.get("/results")
def student_results(semester_id: str | None = None, user: User = Depends(current_user), db: Session = Depends(get_db)):
    student = current_student(user, db)
    query = (select(CourseEnrollment).join(CourseOffering).where(CourseEnrollment.student_id == student.id)
             .options(joinedload(CourseEnrollment.offering).joinedload(CourseOffering.course),
                      joinedload(CourseEnrollment.offering).joinedload(CourseOffering.semester)))
    if semester_id and semester_id != "all":
        query = query.where(CourseOffering.semester_id == semester_id)
    rows = db.scalars(query.join(Semester).order_by(Semester.starts_on.desc(), CourseOffering.course_id)).all()
    results = [{"id": row.id, "course_code": row.offering.course.code, "course_name": row.offering.course.name,
                "credits": row.offering.course.credits, "semester_id": row.offering.semester_id,
                "semester": row.offering.semester.name, "attendance_score": row.attendance_score,
                "midterm_score": row.midterm_score, "final_score": row.final_score, "total_score": row.total_score,
                "letter_grade": row.letter_grade, "status": row.status} for row in rows]
    completed = [row for row in rows if row.status == "Hoàn thành"]
    passed = [row for row in completed if row.total_score is not None and row.total_score >= 5]
    points = {"A": 4.0, "A-": 3.7, "B+": 3.3, "B": 3.0, "B-": 2.7, "C+": 2.3,
              "C": 2.0, "C-": 1.7, "D+": 1.3, "D": 1.0, "F": 0.0}
    graded = [row for row in completed if row.letter_grade in points]
    credits = sum(row.offering.course.credits for row in passed)
    gpa = round(sum(points[row.letter_grade] * row.offering.course.credits for row in graded) /
                sum(row.offering.course.credits for row in graded), 2) if graded else None
    return {"items": results, "credits_earned": credits, "gpa": gpa,
            "failed_courses": [row for row in results if row["status"] == "Hoàn thành" and (row["total_score"] or 0) < 5]}


@router.get("/conduct")
def student_conduct(user: User = Depends(current_user), db: Session = Depends(get_db)):
    student = current_student(user, db)
    rows = db.scalars(select(ConductRecord).join(Semester).where(ConductRecord.student_id == student.id)
                      .options(joinedload(ConductRecord.semester)).order_by(Semester.starts_on.desc())).all()
    return {"items": [{"id": row.id, "semester_id": row.semester_id, "semester": row.semester.name,
                       "score": row.score, "rating": row.rating, "comment": row.comment,
                       "status": row.status, "evaluated_at": row.evaluated_at} for row in rows]}


@router.get("/finance")
def student_finance(user: User = Depends(current_user), db: Session = Depends(get_db)):
    student = current_student(user, db)
    rows = db.scalars(select(StudentCharge).where(StudentCharge.student_id == student.id)
                      .options(joinedload(StudentCharge.semester), joinedload(StudentCharge.transactions))
                      .order_by(StudentCharge.due_date.desc())).unique().all()
    items = []
    for row in rows:
        paid = sum(tx.amount for tx in row.transactions)
        remaining = max(0, row.amount_due - paid)
        state = "Đã thanh toán" if remaining == 0 else "Thanh toán một phần" if paid else "Quá hạn" if row.due_date < date.today() else "Chưa thanh toán"
        items.append({"id": row.id, "semester": row.semester.name, "title": row.title,
                      "amount_due": row.amount_due, "amount_paid": paid, "remaining": remaining,
                      "due_date": row.due_date, "status": state,
                      "transactions": [{"id": tx.id, "amount": tx.amount, "paid_at": tx.paid_at,
                                        "reference": tx.reference, "note": tx.note} for tx in row.transactions]})
    return {"items": items, "total_due": sum(item["amount_due"] for item in items),
            "total_paid": sum(item["amount_paid"] for item in items),
            "total_remaining": sum(item["remaining"] for item in items)}


@router.get("/assignments")
def student_assignments(status: str | None = None, user: User = Depends(current_user), db: Session = Depends(get_db)):
    student = current_student(user, db)
    rows = db.scalars(select(AssignmentSubmission).join(Assignment).join(CourseOffering)
                      .where(AssignmentSubmission.student_id == student.id)
                      .options(joinedload(AssignmentSubmission.assignment).joinedload(Assignment.offering).joinedload(CourseOffering.course),
                               joinedload(AssignmentSubmission.assignment).joinedload(Assignment.offering).joinedload(CourseOffering.semester))
                      .order_by(Assignment.deadline)).all()
    now = datetime.now(timezone.utc)
    items = []
    for row in rows:
        effective = row.status if row.status in {"Đã nộp", "Đã chấm"} else "Quá hạn" if _as_utc(row.assignment.deadline) < now else row.status
        if status and effective != status:
            continue
        items.append({"id": row.assignment.id, "submission_id": row.id, "title": row.assignment.title,
                      "description": row.assignment.description, "course_code": row.assignment.offering.course.code,
                      "course_name": row.assignment.offering.course.name, "semester": row.assignment.offering.semester.name,
                      "assigned_at": row.assignment.assigned_at, "deadline": row.assignment.deadline,
                      "status": effective, "submitted_at": row.submitted_at, "score": row.score,
                      "content": row.content})
    return {"items": items, "count": len(items)}


class SubmissionInput(BaseModel):
    content: str = Field(min_length=1, max_length=10000)


@router.post("/assignments/{assignment_id}/submit")
def submit_assignment(assignment_id: str, data: SubmissionInput, user: User = Depends(current_user), db: Session = Depends(get_db)):
    if not data.content.strip():
        raise HTTPException(status_code=422, detail="Nội dung bài nộp không được để trống.")
    student = current_student(user, db)
    row = db.scalar(select(AssignmentSubmission).join(Assignment)
                    .where(AssignmentSubmission.assignment_id == assignment_id,
                           AssignmentSubmission.student_id == student.id)
                    .options(joinedload(AssignmentSubmission.assignment)))
    if not row:
        raise HTTPException(status_code=404, detail="Không tìm thấy bài tập được giao cho sinh viên này.")
    if row.status == "Đã chấm":
        raise HTTPException(status_code=409, detail="Bài tập đã được chấm, không thể nộp lại.")
    row.content = data.content.strip()
    row.submitted_at = datetime.now(timezone.utc)
    row.status = "Đã nộp"
    db.commit()
    return {"id": row.assignment_id, "status": row.status, "submitted_at": row.submitted_at}


news_router = APIRouter(prefix="/news", tags=["University news and events"])


@news_router.get("")
def list_news(category: str | None = None, q: str | None = None,
              page: int = Query(1, ge=1), page_size: int = Query(9, ge=1, le=50), db: Session = Depends(get_db)):
    from app.models import NewsArticle
    query = select(NewsArticle).where(NewsArticle.status == "published")
    if category:
        query = query.where(NewsArticle.category == category)
    if q:
        query = query.where(NewsArticle.title.ilike(f"%{q[:100]}%") | NewsArticle.summary.ilike(f"%{q[:100]}%"))
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    rows = db.scalars(query.order_by(NewsArticle.published_at.desc()).offset((page - 1) * page_size).limit(page_size)).all()
    categories = db.scalars(select(NewsArticle.category).where(NewsArticle.status == "published").distinct().order_by(NewsArticle.category)).all()
    return {"items": [{"slug": row.slug, "title": row.title, "category": row.category, "summary": row.summary,
                       "image_url": row.image_url, "source_url": row.source_url,
                       "published_at": row.published_at, "status": row.status} for row in rows],
            "categories": categories, "page": page, "page_size": page_size, "total": total,
            "pages": (total + page_size - 1) // page_size}


@news_router.get("/{slug}")
def news_detail(slug: str, db: Session = Depends(get_db)):
    from app.models import NewsArticle
    row = db.scalar(select(NewsArticle).where(NewsArticle.slug == slug, NewsArticle.status == "published"))
    if not row:
        raise HTTPException(status_code=404, detail="Không tìm thấy bài viết.")
    return {"slug": row.slug, "title": row.title, "category": row.category, "summary": row.summary,
            "content": row.content, "image_url": row.image_url, "source_url": row.source_url,
            "published_at": row.published_at, "status": row.status}


@news_router.get("/events/list")
def list_public_events(state: str = Query("upcoming", pattern="^(upcoming|ongoing|past|all)$"),
                       month: str | None = Query(None, pattern=r"^\d{4}-\d{2}$"),
                       db: Session = Depends(get_db)):
    from app.models import UniversityEvent
    now = datetime.now(timezone.utc)
    query = select(UniversityEvent).where(UniversityEvent.status == "published")
    if state == "upcoming":
        query = query.where(UniversityEvent.starts_at > now)
    elif state == "ongoing":
        query = query.where(UniversityEvent.starts_at <= now, UniversityEvent.ends_at >= now)
    elif state == "past":
        query = query.where(UniversityEvent.ends_at < now)
    if month:
        try:
            year, month_number = (int(part) for part in month.split("-"))
            month_start = datetime(year, month_number, 1, tzinfo=timezone.utc)
            month_end = datetime(year + (month_number == 12), 1 if month_number == 12 else month_number + 1, 1, tzinfo=timezone.utc)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail="Tháng cần có định dạng YYYY-MM hợp lệ.") from exc
        query = query.where(UniversityEvent.starts_at < month_end, UniversityEvent.ends_at >= month_start)
    ordering = UniversityEvent.starts_at.desc() if state == "past" else UniversityEvent.starts_at.asc()
    rows = db.scalars(query.order_by(ordering).limit(100)).all()
    return {"items": [{"id": row.id, "title": row.title, "category": row.category, "summary": row.summary,
                       "location": row.location, "starts_at": row.starts_at, "ends_at": row.ends_at,
                       "is_all_day": row.is_all_day, "source_url": row.source_url} for row in rows],
            "state": state, "month": month, "count": len(rows)}


@news_router.get("/events/upcoming")
def upcoming_events(db: Session = Depends(get_db)):
    from app.models import UniversityEvent
    rows = db.scalars(select(UniversityEvent).where(UniversityEvent.status == "published",
                      UniversityEvent.ends_at >= datetime.now(timezone.utc)).order_by(UniversityEvent.starts_at).limit(20)).all()
    return {"items": [{"id": row.id, "title": row.title, "category": row.category, "summary": row.summary,
                       "location": row.location, "starts_at": row.starts_at, "ends_at": row.ends_at,
                       "is_all_day": row.is_all_day, "source_url": row.source_url} for row in rows]}
