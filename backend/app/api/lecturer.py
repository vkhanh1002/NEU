from datetime import date, datetime, timedelta
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.api.deps import current_user
from app.core.database import get_db
from app.models import AttendanceSession, CourseEnrollment, CourseGradeAudit, CourseOffering, Personnel, Semester, Student, User
from app.services.schedule import serialize_schedule

router = APIRouter(prefix="/lecturer", tags=["Lecturer academic services"])


class GradeUpdate(BaseModel):
    attendance_score: float | None = Field(default=None, ge=0, le=10)
    midterm_score: float | None = Field(default=None, ge=0, le=10)
    final_score: float | None = Field(default=None, ge=0, le=10)
    total_score: float | None = Field(default=None, ge=0, le=10)
    letter_grade: Literal["", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "F"] | None = None


class EnrollmentCreate(BaseModel):
    student_number: str = Field(min_length=1, max_length=30)


def current_lecturer(user: User, db: Session) -> Personnel:
    if user.role != "lecturer":
        raise HTTPException(status_code=403, detail="Chức năng chỉ dành cho tài khoản giảng viên.")
    lecturer = db.scalar(select(Personnel).where(Personnel.user_id == user.id, Personnel.kind == "lecturer"))
    if not lecturer:
        raise HTTPException(status_code=404, detail="Tài khoản chưa được liên kết với hồ sơ giảng viên.")
    return lecturer


@router.get("/schedule")
def lecturer_schedule(semester_id: str | None = None, academic_year: str | None = None,
                      course_code: str | None = None, section: str | None = None,
                      user: User = Depends(current_user), db: Session = Depends(get_db)):
    lecturer = current_lecturer(user, db)
    query = (select(CourseOffering).where(CourseOffering.lecturer_id == lecturer.id)
             .options(joinedload(CourseOffering.course), joinedload(CourseOffering.semester),
                      joinedload(CourseOffering.lecturer)))
    if semester_id and semester_id != "all":
        query = query.where(CourseOffering.semester_id == semester_id)
    elif semester_id != "all":
        current_term = select(Semester.id).where(Semester.is_current.is_(True)).limit(1).scalar_subquery()
        query = query.where(CourseOffering.semester_id == current_term)
    if academic_year:
        query = query.join(Semester).where(Semester.academic_year == academic_year)
    if course_code:
        from app.models import Course
        query = query.join(Course).where(Course.code == course_code)
    if section:
        query = query.where(CourseOffering.section == section)
    offerings = db.scalars(query.order_by(CourseOffering.weekday, CourseOffering.starts_at)).all()
    today = date.today()
    rows = [serialize_schedule(item, today) for item in offerings]
    active_weekly = [row for row in rows if row["semester_starts_on"] <= today.isoformat() <= row["semester_ends_on"]]
    today_rows = [row for row in rows if row["class_date"] == today.isoformat()]
    now = datetime.now()
    upcoming = []
    for row in rows:
        class_date = date.fromisoformat(row["class_date"])
        start_time = datetime.strptime(row["starts_at"], "%H:%M").time()
        if class_date == today and start_time <= now.time():
            class_date += timedelta(days=7)
        if class_date <= date.fromisoformat(row["semester_ends_on"]):
            upcoming.append(({**row, "class_date": class_date.isoformat()}, class_date, start_time))
    upcoming.sort(key=lambda item: (item[1], item[2]))
    terms = db.scalars(select(Semester).join(CourseOffering).where(CourseOffering.lecturer_id == lecturer.id).distinct().order_by(Semester.starts_on.desc())).all()
    return {
        "lecturer": {"id": lecturer.id, "code": lecturer.code, "full_name": lecturer.full_name},
        "items": rows,
        "today": today_rows,
        "next_class": upcoming[0][0] if upcoming else None,
        "week_count": len(active_weekly),
        "semesters": [{"id": term.id, "code": term.code, "name": term.name,
                       "academic_year": term.academic_year, "is_current": term.is_current} for term in terms],
        "courses": sorted({(row["course_code"], row["course_name"]) for row in rows}),
        "sections": sorted({row["section"] for row in rows}),
    }


@router.get("/schedule/{offering_id}/students")
def lecturer_offering_students(offering_id: str, q: str = "", page: int = 1, page_size: int = 20,
                               user: User = Depends(current_user), db: Session = Depends(get_db)):
    return _lecturer_roster(offering_id, q, page, page_size, user, db)


def _lecturer_roster(offering_id: str, q: str, page: int, page_size: int, user: User, db: Session):
    lecturer = current_lecturer(user, db)
    offering = db.scalar(select(CourseOffering).where(
        CourseOffering.id == offering_id, CourseOffering.lecturer_id == lecturer.id,
    ).options(joinedload(CourseOffering.course), joinedload(CourseOffering.semester), joinedload(CourseOffering.lecturer)))
    if not offering:
        raise HTTPException(status_code=404, detail="Không tìm thấy lớp học phần được phân công.")
    page = max(1, page); page_size = min(100, max(1, page_size))
    query = select(CourseEnrollment).join(Student).where(CourseEnrollment.offering_id == offering.id)
    count_query = select(func.count(CourseEnrollment.id)).join(Student).where(CourseEnrollment.offering_id == offering.id)
    if q.strip():
        pattern = f"%{q.strip()}%"
        condition = (Student.student_number.ilike(pattern)) | (Student.full_name.ilike(pattern))
        query = query.where(condition); count_query = count_query.where(condition)
    total = db.scalar(count_query) or 0
    rows = db.scalars(query.options(joinedload(CourseEnrollment.student)).order_by(Student.student_number)
                      .offset((page - 1) * page_size).limit(page_size)).all()
    return {
        "offering": {"id": offering.id, "course_code": offering.course.code, "course_name": offering.course.name,
                     "section": offering.section, "section_code": f"{offering.course.code}-{offering.section}",
                     "lecturer_name": offering.lecturer.full_name if offering.lecturer else lecturer.full_name},
        "items": [{"student_id": row.student.id, "student_number": row.student.student_number,
                   "full_name": row.student.full_name, "email": row.student.email,
                   "class_name": row.student.class_name, "status": row.status} for row in rows],
        "count": total, "page": page, "page_size": page_size,
    }


@router.get("/classes/{offering_id}/students")
def lecturer_class_roster(offering_id: str, q: str = "", page: int = 1, page_size: int = 20,
                          user: User = Depends(current_user), db: Session = Depends(get_db)):
    return _lecturer_roster(offering_id, q, page, page_size, user, db)


@router.get("/classes/{offering_id}/students/lookup")
def lookup_student_for_offering(offering_id: str, student_number: str,
                                user: User = Depends(current_user), db: Session = Depends(get_db)):
    offering = _owned_offering(offering_id, user, db)
    student = db.scalar(select(Student).where(func.lower(Student.student_number) == student_number.strip().lower()))
    if not student:
        raise HTTPException(404, "Không tìm thấy sinh viên theo mã đã nhập.")
    if db.scalar(select(CourseEnrollment.id).where(CourseEnrollment.offering_id == offering.id,
                                                   CourseEnrollment.student_id == student.id)):
        raise HTTPException(409, "Sinh viên đã có trong lớp học phần này.")
    return {"student_id": student.id, "student_number": student.student_number,
            "full_name": student.full_name, "email": student.email, "class_name": student.class_name}


@router.post("/classes/{offering_id}/students", status_code=201)
def add_student_to_offering(offering_id: str, body: EnrollmentCreate,
                            user: User = Depends(current_user), db: Session = Depends(get_db)):
    offering = _owned_offering(offering_id, user, db)
    if db.scalar(select(AttendanceSession.id).where(AttendanceSession.offering_id == offering.id,
                                                     AttendanceSession.status == "open")):
        raise HTTPException(409, "Không thể thay đổi danh sách khi lớp đang mở phiên điểm danh.")
    student = db.scalar(select(Student).where(func.lower(Student.student_number) == body.student_number.strip().lower()))
    if not student:
        raise HTTPException(404, "Không tìm thấy sinh viên theo mã đã nhập.")
    if db.scalar(select(CourseEnrollment.id).where(CourseEnrollment.offering_id == offering.id,
                                                   CourseEnrollment.student_id == student.id)):
        raise HTTPException(409, "Sinh viên đã có trong lớp học phần này.")
    enrollment = CourseEnrollment(student_id=student.id, offering_id=offering.id, status="Đang học")
    db.add(enrollment)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Sinh viên đã được thêm vào lớp học phần này.") from None
    return {"student_id": student.id, "student_number": student.student_number,
            "full_name": student.full_name, "email": student.email,
            "class_name": student.class_name, "status": enrollment.status}


def _owned_offering(offering_id: str, user: User, db: Session) -> CourseOffering:
    lecturer = current_lecturer(user, db)
    offering = db.scalar(select(CourseOffering).where(
        CourseOffering.id == offering_id, CourseOffering.lecturer_id == lecturer.id,
    ).options(joinedload(CourseOffering.course)))
    if not offering:
        raise HTTPException(status_code=404, detail="Không tìm thấy lớp học phần được phân công.")
    return offering


@router.get("/classes/{offering_id}/grades")
def lecturer_class_grades(offering_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    offering = _owned_offering(offering_id, user, db)
    rows = db.scalars(select(CourseEnrollment).join(Student).where(CourseEnrollment.offering_id == offering.id)
                      .options(joinedload(CourseEnrollment.student)).order_by(Student.student_number)).all()
    return {"offering": {"id": offering.id, "course_code": offering.course.code,
                          "course_name": offering.course.name, "section": offering.section},
            "items": [{"student_id": row.student_id, "student_number": row.student.student_number,
                       "full_name": row.student.full_name, "class_name": row.student.class_name,
                       "attendance_score": row.attendance_score, "midterm_score": row.midterm_score,
                       "final_score": row.final_score, "total_score": row.total_score,
                       "letter_grade": row.letter_grade} for row in rows]}


@router.patch("/classes/{offering_id}/grades/{student_id}")
def update_lecturer_grade(offering_id: str, student_id: str, body: GradeUpdate,
                          user: User = Depends(current_user), db: Session = Depends(get_db)):
    offering = _owned_offering(offering_id, user, db)
    updates = body.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=422, detail="Nhập ít nhất một trường điểm cần cập nhật.")
    row = db.scalar(select(CourseEnrollment).where(CourseEnrollment.offering_id == offering.id,
                                                    CourseEnrollment.student_id == student_id))
    if row is None:
        raise HTTPException(status_code=404, detail="Sinh viên không thuộc lớp học phần này.")
    keys = ("attendance_score", "midterm_score", "final_score", "total_score", "letter_grade")
    before = {key: getattr(row, key) for key in keys}
    for key, value in updates.items():
        setattr(row, key, value)
    after = {key: getattr(row, key) for key in keys}
    db.add(CourseGradeAudit(enrollment_id=row.id, actor_id=user.id,
                            previous_values=before, new_values=after))
    db.commit()
    return {"student_id": row.student_id, **after, "updated_at": row.updated_at}


@router.get("/classes/{offering_id}/grades/audit")
def lecturer_grade_history(offering_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    offering = _owned_offering(offering_id, user, db)
    rows = db.scalars(select(CourseGradeAudit).join(CourseEnrollment)
                      .where(CourseEnrollment.offering_id == offering.id)
                      .order_by(CourseGradeAudit.created_at.desc()).limit(200)).all()
    return {"items": [{"id": row.id, "student_number": db.get(Student, db.get(CourseEnrollment, row.enrollment_id).student_id).student_number,
                       "actor_id": row.actor_id, "previous_values": row.previous_values,
                       "new_values": row.new_values, "created_at": row.created_at} for row in rows]}
