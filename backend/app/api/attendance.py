from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import current_user
from app.core.database import get_db
from app.models import (
    AttendanceAuditLog, AttendanceEvidence, AttendanceMakeupRequest, AttendanceRecord,
    AttendanceSession, Course, CourseEnrollment, CourseOffering, Personnel, Semester,
    Student, User,
)

router = APIRouter(tags=["Smart attendance"])
UPLOAD_DIR = Path(__import__("os").environ.get("ATTENDANCE_UPLOAD_DIR", str(Path(__file__).resolve().parents[2] / "data" / "attendance")))
MAX_IMAGE_BYTES = 5 * 1024 * 1024
ALLOWED_TYPES = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}


def lecturer_person(user: User, db: Session) -> Personnel:
    if user.role != "lecturer":
        raise HTTPException(403, "Chức năng chỉ dành cho tài khoản giảng viên.")
    row = db.scalar(select(Personnel).where(Personnel.user_id == user.id, Personnel.kind == "lecturer"))
    if row is None:
        raise HTTPException(404, "Tài khoản chưa được liên kết với hồ sơ giảng viên.")
    return row


def student_person(user: User, db: Session) -> Student:
    if user.role != "student":
        raise HTTPException(403, "Chức năng chỉ dành cho tài khoản sinh viên.")
    row = db.scalar(select(Student).where(Student.user_id == user.id))
    if row is None:
        raise HTTPException(404, "Tài khoản chưa được liên kết với hồ sơ sinh viên.")
    return row


def _offering_query():
    return select(CourseOffering).options(joinedload(CourseOffering.course), joinedload(CourseOffering.semester))


def _session_for_lecturer(session_id: str, lecturer: Personnel, db: Session) -> tuple[AttendanceSession, CourseOffering]:
    row = db.scalar(select(AttendanceSession).where(AttendanceSession.id == session_id))
    if row is None:
        raise HTTPException(404, "Không tìm thấy phiên điểm danh.")
    offering = db.scalar(_offering_query().where(
        CourseOffering.id == row.offering_id, CourseOffering.lecturer_id == lecturer.id,
    ))
    if offering is None:
        raise HTTPException(404, "Phiên không thuộc lớp học phần bạn phụ trách.")
    return row, offering


def _session_card(session: AttendanceSession, offering: CourseOffering, db: Session) -> dict:
    totals = db.execute(select(AttendanceRecord.status, func.count(AttendanceRecord.id))
                        .where(AttendanceRecord.session_id == session.id).group_by(AttendanceRecord.status)).all()
    counts = dict(totals)
    return {
        "id": session.id, "offering_id": offering.id, "course_code": offering.course.code,
        "course_name": offering.course.name, "section": offering.section,
        "semester": offering.semester.name, "starts_at": session.starts_at,
        "closed_at": session.closed_at, "status": session.status,
        "present": counts.get("present", 0), "late": counts.get("late", 0),
        "absent": counts.get("absent", 0), "total": sum(counts.values()),
    }


class OpenSessionBody(BaseModel):
    offering_id: str


class MarkAttendanceBody(BaseModel):
    status: str = Field(pattern="^(present|late|absent)$")


class ReviewBody(BaseModel):
    decision: str = Field(pattern="^(accepted|rejected)$")
    reason: str = Field(default="", max_length=1000)


@router.get("/lecturer/classes")
def lecturer_classes(user: User = Depends(current_user), db: Session = Depends(get_db)):
    lecturer = lecturer_person(user, db)
    offerings = db.scalars(_offering_query().join(Semester).where(CourseOffering.lecturer_id == lecturer.id)
                           .order_by(Semester.starts_on.desc(), CourseOffering.weekday, CourseOffering.starts_at)).all()
    items = []
    for offering in offerings:
        count = db.scalar(select(func.count(CourseEnrollment.id)).where(CourseEnrollment.offering_id == offering.id)) or 0
        items.append({"id": offering.id, "course_code": offering.course.code, "course_name": offering.course.name,
                      "section": offering.section, "room": offering.room, "semester": offering.semester.name,
                      "academic_year": offering.semester.academic_year, "weekday": offering.weekday,
                      "starts_at": offering.starts_at.strftime("%H:%M"), "ends_at": offering.ends_at.strftime("%H:%M"),
                      "student_count": count})
    return {"items": items, "count": len(items)}


@router.get("/lecturer/overview")
def lecturer_overview(user: User = Depends(current_user), db: Session = Depends(get_db)):
    lecturer = lecturer_person(user, db)
    offering_ids = select(CourseOffering.id).where(CourseOffering.lecturer_id == lecturer.id)
    classes = db.scalars(select(CourseOffering).options(joinedload(CourseOffering.course), joinedload(CourseOffering.semester))
                         .where(CourseOffering.lecturer_id == lecturer.id)).all()
    students = db.scalar(select(func.count(func.distinct(CourseEnrollment.student_id)))
                         .join(CourseOffering, CourseEnrollment.offering_id == CourseOffering.id)
                         .where(CourseOffering.lecturer_id == lecturer.id)) or 0
    sessions = db.scalars(select(AttendanceSession).where(AttendanceSession.offering_id.in_(offering_ids))).all()
    closed_ids = [row.id for row in sessions if row.status == "closed"]
    attended = db.scalar(select(func.count(AttendanceRecord.id)).where(
        AttendanceRecord.session_id.in_(closed_ids), AttendanceRecord.status.in_(["present", "late"]))) or 0 if closed_ids else 0
    total = db.scalar(select(func.count(AttendanceRecord.id)).where(AttendanceRecord.session_id.in_(closed_ids))) or 0 if closed_ids else 0
    pending = db.scalar(select(func.count(AttendanceMakeupRequest.id)).join(AttendanceRecord)
                         .join(AttendanceSession).join(CourseOffering)
                         .where(CourseOffering.lecturer_id == lecturer.id, AttendanceMakeupRequest.status == "pending")) or 0
    now = datetime.now(timezone.utc)
    return {"lecturer": lecturer.full_name, "class_count": len(classes), "student_count": students,
            "sessions_count": len(sessions), "pending_requests": pending,
            "attendance_rate": round(attended / total * 100) if total else None,
            "today": [{"id": row.id, "course": row.course.name, "code": row.course.code, "section": row.section,
                       "room": row.room, "starts_at": row.starts_at.strftime("%H:%M"), "ends_at": row.ends_at.strftime("%H:%M")}
                      for row in classes if row.weekday == now.isoweekday() and row.semester.is_current]}


@router.post("/lecturer/attendance/sessions", status_code=201)
def open_attendance(body: OpenSessionBody, user: User = Depends(current_user), db: Session = Depends(get_db)):
    lecturer = lecturer_person(user, db)
    offering = db.scalar(_offering_query().where(
        CourseOffering.id == body.offering_id, CourseOffering.lecturer_id == lecturer.id,
    ))
    if offering is None:
        raise HTTPException(404, "Không tìm thấy lớp học phần được phân công.")
    if db.scalar(select(AttendanceSession.id).where(AttendanceSession.offering_id == offering.id,
                                                    AttendanceSession.status == "open")):
        raise HTTPException(409, "Lớp này đang có phiên điểm danh mở.")
    enrollments = db.scalars(select(CourseEnrollment).where(CourseEnrollment.offering_id == offering.id)).all()
    if not enrollments:
        raise HTTPException(409, "Chưa có sinh viên đăng ký lớp học phần này.")
    session = AttendanceSession(offering_id=offering.id, opened_by=user.id, starts_at=datetime.now(timezone.utc), status="open")
    db.add(session)
    db.flush()
    for enrollment in enrollments:
        db.add(AttendanceRecord(session_id=session.id, student_id=enrollment.student_id, status="absent"))
    db.add(AttendanceAuditLog(session_id=session.id, actor_id=user.id, action="session_opened",
                              details={"offering_id": offering.id, "roster_size": len(enrollments)}))
    db.commit()
    return _session_card(session, offering, db)


@router.get("/lecturer/attendance/sessions")
def lecturer_sessions(user: User = Depends(current_user), db: Session = Depends(get_db)):
    lecturer = lecturer_person(user, db)
    sessions = db.scalars(select(AttendanceSession).join(CourseOffering)
                          .where(CourseOffering.lecturer_id == lecturer.id)
                          .order_by(AttendanceSession.starts_at.desc())).all()
    return {"items": [_session_card(row, db.scalar(_offering_query().where(CourseOffering.id == row.offering_id)), db)
                       for row in sessions]}


@router.get("/lecturer/attendance/sessions/{session_id}")
def lecturer_session_detail(session_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    lecturer = lecturer_person(user, db)
    session, offering = _session_for_lecturer(session_id, lecturer, db)
    rows = db.scalars(select(AttendanceRecord).join(Student, AttendanceRecord.student_id == Student.id)
                      .where(AttendanceRecord.session_id == session.id)
                      .options(joinedload(AttendanceRecord.student)).order_by(Student.student_number)).all()
    evidence = {row.student_id: row for row in db.scalars(select(AttendanceEvidence).where(AttendanceEvidence.session_id == session.id)).all()}
    return {**_session_card(session, offering, db), "items": [
        {"record_id": row.id, "student_id": row.student_id, "student_number": row.student.student_number,
         "full_name": row.student.full_name, "class_name": row.student.class_name, "status": row.status,
         "marked_at": row.marked_at, "evidence_id": evidence[row.student_id].id if row.student_id in evidence else None}
        for row in rows]}


@router.patch("/lecturer/attendance/sessions/{session_id}/students/{student_id}")
def mark_attendance(session_id: str, student_id: str, body: MarkAttendanceBody,
                    user: User = Depends(current_user), db: Session = Depends(get_db)):
    lecturer = lecturer_person(user, db)
    session, _ = _session_for_lecturer(session_id, lecturer, db)
    if session.status != "open":
        raise HTTPException(409, "Phiên điểm danh đã kết thúc.")
    row = db.scalar(select(AttendanceRecord).where(AttendanceRecord.session_id == session.id,
                                                   AttendanceRecord.student_id == student_id))
    if row is None:
        raise HTTPException(404, "Sinh viên không thuộc danh sách lớp học phần.")
    previous = row.status
    row.status = body.status
    row.marked_at = datetime.now(timezone.utc)
    row.marked_by = user.id
    db.add(AttendanceAuditLog(session_id=session.id, record_id=row.id, actor_id=user.id, action="record_marked",
                              details={"from": previous, "to": body.status}))
    db.commit()
    return {"record_id": row.id, "status": row.status, "marked_at": row.marked_at}


@router.post("/lecturer/attendance/sessions/{session_id}/close")
def close_attendance(session_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    lecturer = lecturer_person(user, db)
    session, offering = _session_for_lecturer(session_id, lecturer, db)
    if session.status != "open":
        raise HTTPException(409, "Phiên điểm danh đã kết thúc.")
    session.status = "closed"
    session.closed_at = datetime.now(timezone.utc)
    db.add(AttendanceAuditLog(session_id=session.id, actor_id=user.id, action="session_closed", details={}))
    db.commit()
    return _session_card(session, offering, db)


@router.get("/student/attendance")
def student_attendance(user: User = Depends(current_user), db: Session = Depends(get_db)):
    student = student_person(user, db)
    records = db.scalars(select(AttendanceRecord).join(AttendanceSession).join(CourseOffering)
                         .where(AttendanceRecord.student_id == student.id)
                         .options(joinedload(AttendanceRecord.session), joinedload(AttendanceRecord.student))
                         .order_by(AttendanceSession.starts_at.desc())).all()
    items = []
    for record in records:
        session = record.session
        offering = db.scalar(_offering_query().where(CourseOffering.id == session.offering_id))
        evidence = db.scalar(select(AttendanceEvidence).where(AttendanceEvidence.session_id == session.id,
                                                               AttendanceEvidence.student_id == student.id))
        request = db.scalar(select(AttendanceMakeupRequest).where(AttendanceMakeupRequest.record_id == record.id))
        items.append({"record_id": record.id, "session_id": session.id, "course_code": offering.course.code,
                      "course_name": offering.course.name, "section": offering.section, "starts_at": session.starts_at,
                      "closed_at": session.closed_at, "session_status": session.status, "status": record.status,
                      "evidence_id": evidence.id if evidence else None,
                      "evidence_received_at": evidence.received_at if evidence else None,
                      "makeup_request": {"status": request.status, "reason": request.review_reason,
                                         "submitted_at": request.submitted_at} if request else None,
                      "can_submit_request": bool(session.status == "closed" and record.status == "absent" and evidence and not request)})
    closed = [row for row in records if row.session.status == "closed"]
    present = sum(row.status == "present" for row in closed)
    late = sum(row.status == "late" for row in closed)
    absent = sum(row.status == "absent" for row in closed)
    return {"items": items, "count": len(items),
            "summary": {"completed_sessions": len(closed), "present": present, "late": late,
                        "absent": absent, "participation_rate": round((present + late) / len(closed) * 100) if closed else None}}


@router.post("/student/attendance/sessions/{session_id}/evidence", status_code=201)
async def capture_attendance_evidence(session_id: str, photo: UploadFile = File(...),
                                      user: User = Depends(current_user), db: Session = Depends(get_db)):
    student = student_person(user, db)
    session = db.scalar(select(AttendanceSession).where(AttendanceSession.id == session_id).with_for_update())
    if session is None or session.status != "open":
        raise HTTPException(409, "Chỉ có thể gửi ảnh khi phiên điểm danh đang diễn ra.")
    enrolled = db.scalar(select(CourseEnrollment.id).where(CourseEnrollment.student_id == student.id,
                                                           CourseEnrollment.offering_id == session.offering_id))
    if not enrolled:
        raise HTTPException(403, "Bạn không thuộc lớp học phần của phiên này.")
    media_type = (photo.content_type or "").lower()
    if media_type not in ALLOWED_TYPES:
        raise HTTPException(415, "Ảnh phải ở định dạng JPEG, PNG hoặc WebP.")
    content = await photo.read(MAX_IMAGE_BYTES + 1)
    if not content or len(content) > MAX_IMAGE_BYTES:
        raise HTTPException(413, "Ảnh phải có dung lượng từ 1 byte đến 5 MB.")
    if not content.startswith((b"\xff\xd8\xff", b"\x89PNG\r\n\x1a\n", b"RIFF")):
        raise HTTPException(415, "Tệp gửi lên không phải ảnh hợp lệ.")
    record = db.scalar(select(AttendanceRecord).where(AttendanceRecord.session_id == session.id,
                                                     AttendanceRecord.student_id == student.id))
    if record is None:
        raise HTTPException(403, "Không tìm thấy lượt điểm danh của bạn trong lớp này.")
    if db.scalar(select(AttendanceEvidence.id).where(AttendanceEvidence.session_id == session.id,
                                                     AttendanceEvidence.student_id == student.id)):
        raise HTTPException(409, "Đã nhận ảnh minh chứng cho buổi học này.")
    # The receipt time is assigned by the server after it has read the uploaded bytes.
    received_at = datetime.now(timezone.utc)
    evidence_id = str(uuid4())
    filename = f"{evidence_id}{ALLOWED_TYPES[media_type]}"
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    (UPLOAD_DIR / filename).write_bytes(content)
    evidence = AttendanceEvidence(id=evidence_id, session_id=session.id, student_id=student.id,
                                  storage_path=filename, media_type=media_type, received_at=received_at)
    db.add(evidence)
    db.add(AttendanceAuditLog(session_id=session.id, record_id=record.id, actor_id=user.id,
                              action="evidence_received", details={"evidence_id": evidence_id, "received_at": received_at.isoformat()}))
    try:
        db.commit()
    except Exception:
        db.rollback()
        (UPLOAD_DIR / filename).unlink(missing_ok=True)
        raise HTTPException(409, "Ảnh minh chứng đã được gửi cho buổi học này.") from None
    return {"id": evidence.id, "received_at": evidence.received_at, "status": "received"}


@router.post("/student/attendance/records/{record_id}/makeup-requests", status_code=201)
def create_makeup_request(record_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    student = student_person(user, db)
    record = db.scalar(select(AttendanceRecord).where(AttendanceRecord.id == record_id,
                                                     AttendanceRecord.student_id == student.id))
    if record is None:
        raise HTTPException(404, "Không tìm thấy lượt điểm danh của bạn.")
    session = db.get(AttendanceSession, record.session_id)
    if record.status != "absent" or session.status != "closed":
        raise HTTPException(409, "Chỉ gửi yêu cầu cho buổi đã kết thúc và đang có trạng thái Vắng.")
    evidence = db.scalar(select(AttendanceEvidence).where(AttendanceEvidence.session_id == session.id,
                                                           AttendanceEvidence.student_id == student.id))
    if evidence is None or evidence.received_at > (session.closed_at or datetime.min.replace(tzinfo=timezone.utc)):
        raise HTTPException(409, "Cần có ảnh được máy chủ tiếp nhận trong thời gian buổi học.")
    if db.scalar(select(AttendanceMakeupRequest.id).where(AttendanceMakeupRequest.record_id == record.id)):
        raise HTTPException(409, "Bạn đã gửi yêu cầu cho buổi học này.")
    request = AttendanceMakeupRequest(record_id=record.id, evidence_id=evidence.id)
    db.add(request)
    db.add(AttendanceAuditLog(session_id=session.id, record_id=record.id, actor_id=user.id,
                              action="makeup_requested", details={"evidence_id": evidence.id}))
    db.commit()
    return {"id": request.id, "status": request.status, "submitted_at": request.submitted_at}


@router.get("/lecturer/attendance/requests")
def lecturer_makeup_requests(user: User = Depends(current_user), db: Session = Depends(get_db)):
    lecturer = lecturer_person(user, db)
    rows = db.scalars(select(AttendanceMakeupRequest).join(AttendanceRecord).join(AttendanceSession)
                      .join(CourseOffering).where(CourseOffering.lecturer_id == lecturer.id)
                          .order_by(case((AttendanceMakeupRequest.status == "pending", 0), else_=1),
                                    AttendanceMakeupRequest.submitted_at.desc())
                      .options(joinedload(AttendanceMakeupRequest.evidence))).all()
    items = []
    for request in rows:
        record = db.get(AttendanceRecord, request.record_id)
        session = db.get(AttendanceSession, record.session_id)
        student = db.get(Student, record.student_id)
        offering = db.scalar(_offering_query().where(CourseOffering.id == session.offering_id))
        minutes_late = max(0, int((request.evidence.received_at - session.starts_at).total_seconds() // 60))
        items.append({"id": request.id, "status": request.status, "reason": request.review_reason,
                      "student_id": student.id, "student_number": student.student_number, "full_name": student.full_name,
                      "course_code": offering.course.code, "course_name": offering.course.name, "section": offering.section,
                      "starts_at": session.starts_at, "received_at": request.evidence.received_at,
                      "minutes_late": minutes_late, "submitted_at": request.submitted_at,
                      "attendance_status": record.status, "evidence_id": request.evidence_id})
    return {"items": items}


@router.patch("/lecturer/attendance/requests/{request_id}")
def review_makeup_request(request_id: str, body: ReviewBody, user: User = Depends(current_user), db: Session = Depends(get_db)):
    lecturer = lecturer_person(user, db)
    request = db.scalar(select(AttendanceMakeupRequest).where(AttendanceMakeupRequest.id == request_id))
    if request is None:
        raise HTTPException(404, "Không tìm thấy yêu cầu.")
    record = db.get(AttendanceRecord, request.record_id)
    session, _ = _session_for_lecturer(record.session_id, lecturer, db)
    if request.status != "pending":
        raise HTTPException(409, "Yêu cầu đã được xử lý.")
    old_status = record.status
    request.status = body.decision
    request.reviewed_by = user.id
    request.reviewed_at = datetime.now(timezone.utc)
    request.review_reason = body.reason.strip() if body.decision == "rejected" else ""
    if body.decision == "accepted":
        if record.status != "absent":
            raise HTTPException(409, "Lượt điểm danh đã được cập nhật; không thể chấp nhận yêu cầu.")
        record.status = "late"
        record.marked_at = request.evidence.received_at
        record.marked_by = user.id
    db.add(AttendanceAuditLog(session_id=session.id, record_id=record.id, actor_id=user.id,
                              action=f"makeup_{body.decision}",
                              details={"from": old_status, "to": record.status, "reason": request.review_reason}))
    db.commit()
    return {"id": request.id, "status": request.status, "attendance_status": record.status,
            "reviewed_at": request.reviewed_at, "reason": request.review_reason}


@router.get("/attendance/evidence/{evidence_id}")
def get_attendance_evidence(evidence_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    evidence = db.get(AttendanceEvidence, evidence_id)
    if evidence is None:
        raise HTTPException(404, "Không tìm thấy ảnh minh chứng.")
    allowed = user.role == "super_admin"
    if user.role == "student":
        student = student_person(user, db)
        allowed = evidence.student_id == student.id
    elif user.role == "lecturer":
        lecturer = lecturer_person(user, db)
        session = db.get(AttendanceSession, evidence.session_id)
        allowed = bool(session and db.scalar(select(CourseOffering.id).where(
            CourseOffering.id == session.offering_id, CourseOffering.lecturer_id == lecturer.id)))
    if not allowed:
        raise HTTPException(403, "Bạn không có quyền xem ảnh minh chứng này.")
    target = UPLOAD_DIR / Path(evidence.storage_path).name
    if not target.is_file():
        raise HTTPException(404, "Tệp ảnh minh chứng không có trong vùng lưu trữ.")
    return FileResponse(target, media_type=evidence.media_type, filename=target.name)


@router.get("/admin/attendance")
def admin_attendance(user: User = Depends(current_user), db: Session = Depends(get_db)):
    if user.role != "super_admin":
        raise HTTPException(403, "Chức năng chỉ dành cho quản trị viên.")
    sessions = db.scalars(select(AttendanceSession).order_by(AttendanceSession.starts_at.desc()).limit(100)).all()
    items = []
    for session in sessions:
        offering = db.scalar(_offering_query().where(CourseOffering.id == session.offering_id))
        items.append(_session_card(session, offering, db))
    logs = db.scalars(select(AttendanceAuditLog).order_by(AttendanceAuditLog.created_at.desc()).limit(100)).all()
    requests = db.scalars(select(AttendanceMakeupRequest).order_by(AttendanceMakeupRequest.submitted_at.desc()).limit(200)).all()
    request_items = []
    for request in requests:
        record = db.get(AttendanceRecord, request.record_id)
        session = db.get(AttendanceSession, record.session_id)
        student = db.get(Student, record.student_id)
        offering = db.scalar(_offering_query().where(CourseOffering.id == session.offering_id))
        request_items.append({"id": request.id, "status": request.status, "reason": request.review_reason,
                              "student_number": student.student_number, "student_name": student.full_name,
                              "course_code": offering.course.code, "course_name": offering.course.name,
                              "section": offering.section, "session_id": session.id,
                              "evidence_id": request.evidence_id, "submitted_at": request.submitted_at,
                              "reviewed_at": request.reviewed_at, "reviewed_by": request.reviewed_by,
                              "attendance_status": record.status})
    return {"sessions": items, "requests": request_items, "audit": [{"id": row.id, "session_id": row.session_id, "record_id": row.record_id,
            "actor_id": row.actor_id, "action": row.action, "details": row.details, "created_at": row.created_at} for row in logs]}


@router.get("/admin/attendance/requests")
def admin_attendance_requests(user: User = Depends(current_user), db: Session = Depends(get_db)):
    if user.role != "super_admin":
        raise HTTPException(403, "Chức năng chỉ dành cho quản trị viên.")
    rows = db.scalars(select(AttendanceMakeupRequest).order_by(AttendanceMakeupRequest.submitted_at.desc()).limit(200)).all()
    return {"items": [{"id": row.id, "status": row.status, "reason": row.review_reason,
                       "record_id": row.record_id, "submitted_at": row.submitted_at,
                       "reviewed_at": row.reviewed_at, "reviewed_by": row.reviewed_by} for row in rows]}
