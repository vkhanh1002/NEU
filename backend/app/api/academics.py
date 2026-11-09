from datetime import datetime, timezone
from io import BytesIO
from pathlib import PurePosixPath
from urllib.parse import quote
import zipfile

from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.api.deps import current_user, optional_current_user, require_roles
from app.core.database import get_db
from app.core.security import hash_password
from app.models import Applicant, ApplicantDocument, ApplicantPreference, Faculty, Major, Notification, Student, User
from app.schemas import ApplicantCreate, ApplicantPublic, ApplicantStatusUpdate, MajorPublic, StudentProfileUpdate, StudentPublic
from app.services.serializers import applicant_public, student_public

router = APIRouter(tags=["Admissions and profiles"])
STAFF = ("super_admin", "support_staff", "academic_staff")
ADMISSION_STAFF = ("super_admin", "admission_staff")


def major_public(major: Major) -> dict:
    return {"id": major.id, "code": major.code, "name": major.name, "description": major.description,
            "faculty_name": major.faculty.name, "duration_years": major.duration_years,
            "tuition_per_year_vnd": major.tuition_per_year_vnd, "admission_quota": major.admission_quota,
            "admission_status": major.admission_status, "is_demo": major.is_demo}


@router.get("/majors", response_model=list[MajorPublic])
def list_majors(db: Session = Depends(get_db)):
    return [major_public(row) for row in db.scalars(select(Major).options(joinedload(Major.faculty)).order_by(Major.code)).all()]


@router.get("/faculties")
def list_faculties(db: Session = Depends(get_db)):
    return [{"id": row.id, "name": row.name} for row in db.scalars(select(Faculty).order_by(Faculty.name)).all()]


@router.get("/admissions/applications", response_model=list[ApplicantPublic])
def list_applications(_user: User = Depends(require_roles(*ADMISSION_STAFF)), db: Session = Depends(get_db)):
    rows = db.scalars(select(Applicant).options(joinedload(Applicant.major)).order_by(Applicant.created_at.desc())).all()
    return [applicant_public(row) for row in rows]


@router.post("/admissions/applications", response_model=ApplicantPublic, status_code=201)
def create_application(data: ApplicantCreate, user: User | None = Depends(optional_current_user), db: Session = Depends(get_db)):
    if not data.confirmed:
        raise HTTPException(status_code=422, detail="Hãy xác nhận thông tin trước khi gửi hồ sơ.")
    major = db.get(Major, data.desired_major_id)
    if not major or major.admission_status != "Đang tuyển sinh":
        raise HTTPException(status_code=400, detail="Ngành không mở nhận hồ sơ trong dữ liệu hiện tại.")
    email = data.email.lower()
    # Serialize submissions for the same email so two quick/retried public
    # requests cannot pass the duplicate check at the same time on PostgreSQL.
    if db.get_bind().dialect.name == "postgresql":
        db.execute(text("SELECT pg_advisory_xact_lock(hashtext(:email))"), {"email": email})
    if db.scalar(select(Applicant.id).where(Applicant.email == email)):
        raise HTTPException(status_code=409, detail="Email này đã có hồ sơ. Đăng nhập để theo dõi hồ sơ hiện có.")
    existing_user = db.scalar(select(User).where(User.email == email))
    if user and user.role == "applicant" and user.email != email:
        raise HTTPException(status_code=403, detail="Tài khoản thí sinh chỉ được gửi hồ sơ cho email đã đăng nhập.")
    if existing_user and existing_user.role != "applicant":
        raise HTTPException(status_code=409, detail="Email đã được dùng cho tài khoản khác.")
    if existing_user and (user is None or user.id != existing_user.id):
        raise HTTPException(status_code=409, detail="Email đã có tài khoản thí sinh. Đăng nhập để gửi hồ sơ.")
    preference_ids = data.preferences or [data.desired_major_id]
    if preference_ids[0] != data.desired_major_id:
        raise HTTPException(status_code=422, detail="Nguyện vọng đầu tiên cần khớp với ngành đăng ký chính.")
    available_majors = db.scalars(select(Major).where(Major.id.in_(preference_ids), Major.admission_status == "Đang tuyển sinh")).all()
    if len(available_majors) != len(preference_ids):
        raise HTTPException(status_code=422, detail="Một hoặc nhiều ngành trong nguyện vọng không mở nhận hồ sơ.")
    major_by_id = {row.id: row for row in available_majors}
    applicant_values = data.model_dump(exclude={"email", "password", "preferences", "confirmed"})
    try:
        if not existing_user:
            if not data.password:
                raise HTTPException(status_code=422, detail="Tạo mật khẩu để theo dõi hồ sơ sau khi gửi.")
            existing_user = User(email=email, full_name=data.full_name, password_hash=hash_password(data.password), role="applicant")
            db.add(existing_user)
        applicant = Applicant(**applicant_values, email=email)
        db.add(applicant)
        db.flush()
        for order, major_id in enumerate(preference_ids, start=1):
            preference_major = major_by_id[major_id]
            db.add(ApplicantPreference(applicant_id=applicant.id, major_id=major_id,
                                       preference_order=order, program_name=preference_major.name,
                                       admission_method=data.admission_method))
        db.commit()
    except IntegrityError:
        db.rollback()
        if db.scalar(select(Applicant.id).where(Applicant.email == email)):
            raise HTTPException(status_code=409, detail="Email này đã có hồ sơ. Đăng nhập để theo dõi hồ sơ hiện có.") from None
        if db.scalar(select(User.id).where(User.email == email)):
            raise HTTPException(status_code=409, detail="Email đã có tài khoản. Đăng nhập để gửi hoặc theo dõi hồ sơ.") from None
        raise
    db.refresh(applicant)
    return applicant_public(db.scalar(select(Applicant).where(Applicant.id == applicant.id).options(joinedload(Applicant.major))))


@router.get("/admissions/applications/me", response_model=list[ApplicantPublic])
def my_applications(user: User = Depends(require_roles("applicant")), db: Session = Depends(get_db)):
    rows = db.scalars(select(Applicant).where(Applicant.email == user.email)
                      .options(joinedload(Applicant.major)).order_by(Applicant.created_at.desc())).all()
    return [applicant_public(row) for row in rows]


@router.patch("/admissions/applications/{applicant_id}/status", response_model=ApplicantPublic)
def update_application_status(applicant_id: str, data: ApplicantStatusUpdate,
                              _user: User = Depends(require_roles("super_admin", "admission_staff")),
                              db: Session = Depends(get_db)):
    if data.status not in {"Mới tiếp nhận", "Đang xét duyệt", "Cần bổ sung", "Đã duyệt", "Trúng tuyển", "Không đủ điều kiện", "Không trúng tuyển"}:
        raise HTTPException(status_code=422, detail="Trạng thái hồ sơ không hợp lệ.")
    applicant = db.scalar(select(Applicant).where(Applicant.id == applicant_id).options(joinedload(Applicant.major)))
    if not applicant:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ.")
    applicant.status = data.status
    if data.note is not None:
        applicant.review_note = data.note.strip()
    account = db.scalar(select(User).where(User.email == applicant.email))
    if account:
        db.add(Notification(owner_id=account.id, title="Cập nhật hồ sơ tuyển sinh",
                            message=f"Hồ sơ {applicant.full_name}: {applicant.status}" +
                                    (f" · {applicant.review_note}" if applicant.review_note else ""),
                            href="/admissions"))
    db.commit()
    db.refresh(applicant)
    return applicant_public(applicant)


@router.post("/admissions/applications/{applicant_id}/promote", response_model=StudentPublic)
def promote_applicant(applicant_id: str, _user: User = Depends(require_roles("super_admin", "admission_staff")),
                      db: Session = Depends(get_db)):
    applicant = db.scalar(select(Applicant).where(Applicant.id == applicant_id).options(joinedload(Applicant.major)))
    if not applicant:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ.")
    if applicant.status != "Trúng tuyển":
        raise HTTPException(status_code=409, detail="Chỉ có thể chuyển hồ sơ đã trúng tuyển thành sinh viên.")
    if applicant.student_id:
        return student_public(db.scalar(select(Student).where(Student.id == applicant.student_id).options(joinedload(Student.major))))
    account = db.scalar(select(User).where(User.email == applicant.email))
    if account and account.role not in {"applicant", "student"}:
        raise HTTPException(status_code=409, detail="Tài khoản gắn với email hồ sơ không thể chuyển thành sinh viên.")
    linked_student = db.scalar(select(Student).where(Student.user_id == account.id)) if account else None
    if linked_student:
        applicant.student_id = linked_student.id
        db.commit()
        return student_public(db.scalar(select(Student).where(Student.id == linked_student.id).options(joinedload(Student.major))))
    count = db.scalar(select(func.count(Student.id))) or 0
    student = Student(
        user_id=account.id if account else None, applicant_id=applicant.id,
        student_number=f"STU{2026}{count + 1:04d}",
        full_name=applicant.full_name, email=applicant.email, phone=applicant.phone,
        date_of_birth=applicant.date_of_birth, address=applicant.address, major_id=applicant.desired_major_id,
        cohort="2026", enrollment_date=None, is_demo=False,
    )
    db.add(student)
    if account:
        account.role = "student"
        account.full_name = applicant.full_name
    db.flush()
    applicant.student_id = student.id
    db.commit()
    db.refresh(student)
    return student_public(db.scalar(select(Student).where(Student.id == student.id).options(joinedload(Student.major))))


@router.get("/profiles/students", response_model=list[StudentPublic])
def list_students(user: User = Depends(current_user), db: Session = Depends(get_db)):
    query = select(Student).options(joinedload(Student.major)).order_by(Student.student_number)
    if user.role == "student":
        query = query.where(Student.user_id == user.id)
    elif user.role not in STAFF:
        raise HTTPException(status_code=403, detail="Bạn không có quyền xem hồ sơ sinh viên.")
    return [student_public(row) for row in db.scalars(query).all()]


@router.get("/profiles/me", response_model=StudentPublic)
def my_student_profile(user: User = Depends(current_user), db: Session = Depends(get_db)):
    if user.role != "student":
        raise HTTPException(status_code=403, detail="Chức năng chỉ dành cho tài khoản sinh viên.")
    student = db.scalar(select(Student).where(Student.user_id == user.id).options(joinedload(Student.major)))
    if not student:
        raise HTTPException(status_code=404, detail="Tài khoản chưa được liên kết với hồ sơ sinh viên.")
    return student_public(student)


@router.patch("/profiles/me", response_model=StudentPublic)
def update_my_student_profile(data: StudentProfileUpdate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    if user.role != "student":
        raise HTTPException(status_code=403, detail="Chức năng chỉ dành cho tài khoản sinh viên.")
    student = db.scalar(select(Student).where(Student.user_id == user.id).options(joinedload(Student.major)))
    if not student:
        raise HTTPException(status_code=404, detail="Tài khoản chưa được liên kết với hồ sơ sinh viên.")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(student, field, value)
    db.commit()
    return student_public(db.scalar(select(Student).where(Student.id == student.id).options(joinedload(Student.major))))


@router.patch("/profiles/students/{student_id}", response_model=StudentPublic)
def update_student_profile(student_id: str, data: StudentProfileUpdate,
                           _user: User = Depends(require_roles("super_admin")), db: Session = Depends(get_db)):
    student = db.scalar(select(Student).where(Student.id == student_id).options(joinedload(Student.major)))
    if not student:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ sinh viên.")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(student, field, value)
    db.commit()
    return student_public(db.scalar(select(Student).where(Student.id == student.id).options(joinedload(Student.major))))


document_router = APIRouter(tags=["Applicant documents"])
MAX_DOCUMENT_BYTES = 10 * 1024 * 1024
DOCUMENT_TYPES = {
    "cccd_front", "cccd_back", "portrait", "transcript", "graduation_proof",
    "exam_result", "language_certificate", "international_certificate",
    "academic_achievement", "priority_proof", "other",
}
DOCUMENT_REVIEW_STATES = {"Chờ kiểm tra", "Đã xác nhận", "Cần bổ sung"}
DOCUMENT_STAFF = ("super_admin", "admission_staff")
MIME_BY_EXTENSION = {
    ".pdf": "application/pdf", ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
}


def _applicant_document_access(applicant_id: str, user: User, db: Session) -> Applicant:
    applicant = db.get(Applicant, applicant_id)
    if not applicant:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ tuyển sinh.")
    if user.role == "applicant" and applicant.email == user.email:
        return applicant
    if user.role in DOCUMENT_STAFF:
        return applicant
    raise HTTPException(status_code=403, detail="Bạn không có quyền truy cập tài liệu hồ sơ này.")


def _document_public(row: ApplicantDocument) -> dict:
    return {"id": row.id, "document_type": row.document_type, "filename": row.filename,
            "media_type": row.media_type, "size_bytes": row.size_bytes, "status": row.status,
            "review_note": row.review_note, "uploaded_at": row.created_at, "reviewed_at": row.reviewed_at}


def _validate_document(ext: str, content: bytes) -> None:
    if ext == ".pdf" and content.startswith(b"%PDF-"):
        return
    if ext == ".png" and content.startswith(b"\x89PNG\r\n\x1a\n"):
        return
    if ext in {".jpg", ".jpeg"} and content.startswith(b"\xff\xd8\xff"):
        return
    if ext == ".docx":
        try:
            with zipfile.ZipFile(BytesIO(content)) as archive:
                names = set(archive.namelist())
                if ("[Content_Types].xml" in names and "word/document.xml" in names
                        and not any(name.lower().endswith("vbaproject.bin") for name in names)
                        and all(item.file_size <= 50 * 1024 * 1024 for item in archive.infolist())):
                    return
        except (OSError, zipfile.BadZipFile, zipfile.LargeZipFile):
            pass
    raise HTTPException(status_code=415, detail="Định dạng tệp không khớp nội dung hoặc không được hỗ trợ.")


@document_router.get("/admissions/applications/{applicant_id}/documents")
def list_applicant_documents(applicant_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    _applicant_document_access(applicant_id, user, db)
    rows = db.scalars(select(ApplicantDocument).where(ApplicantDocument.applicant_id == applicant_id)
                      .order_by(ApplicantDocument.created_at.desc())).all()
    return [_document_public(row) for row in rows]


@document_router.post("/admissions/applications/{applicant_id}/documents", status_code=201)
async def upload_applicant_document(applicant_id: str, document_type: str = Form(...), file: UploadFile = File(...),
                                    user: User = Depends(current_user), db: Session = Depends(get_db)):
    applicant = _applicant_document_access(applicant_id, user, db)
    if document_type not in DOCUMENT_TYPES:
        raise HTTPException(status_code=422, detail="Loại tài liệu không hợp lệ.")
    if user.role == "applicant" and applicant.status in {"Trúng tuyển", "Không đủ điều kiện", "Không trúng tuyển"}:
        raise HTTPException(status_code=409, detail="Hồ sơ đã kết thúc xử lý nên không thể tải thêm tài liệu.")
    filename = PurePosixPath((file.filename or "").replace("\\", "/")).name
    filename = "".join(character for character in filename if character >= " " and character not in "\r\n")[:255]
    extension = PurePosixPath(filename).suffix.lower()
    if not filename or extension not in MIME_BY_EXTENSION:
        raise HTTPException(status_code=415, detail="Chỉ nhận PDF, DOCX, PNG hoặc JPG/JPEG.")
    content = await file.read(MAX_DOCUMENT_BYTES + 1)
    if not content:
        raise HTTPException(status_code=400, detail="Tệp tải lên đang trống.")
    if len(content) > MAX_DOCUMENT_BYTES:
        raise HTTPException(status_code=413, detail="Mỗi tài liệu tối đa 10 MB.")
    _validate_document(extension, content)
    row = ApplicantDocument(applicant_id=applicant.id, uploaded_by=user.id, document_type=document_type,
                            filename=filename, media_type=MIME_BY_EXTENSION[extension],
                            size_bytes=len(content), content=content, status="Chờ kiểm tra")
    db.add(row)
    db.commit()
    db.refresh(row)
    return _document_public(row)


@document_router.get("/admissions/applications/{applicant_id}/documents/{document_id}/download")
def download_applicant_document(applicant_id: str, document_id: str,
                                user: User = Depends(current_user), db: Session = Depends(get_db)):
    _applicant_document_access(applicant_id, user, db)
    row = db.scalar(select(ApplicantDocument).where(ApplicantDocument.id == document_id,
                                                   ApplicantDocument.applicant_id == applicant_id))
    if not row:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài liệu.")
    return Response(content=row.content, media_type="application/octet-stream",
                    headers={"Content-Disposition": f"attachment; filename*=UTF-8''{quote(row.filename, safe='')}",
                             "X-Content-Type-Options": "nosniff", "Cache-Control": "private, no-store"})


@document_router.delete("/admissions/applications/{applicant_id}/documents/{document_id}", status_code=204)
def delete_applicant_document(applicant_id: str, document_id: str,
                              user: User = Depends(current_user), db: Session = Depends(get_db)):
    applicant = _applicant_document_access(applicant_id, user, db)
    row = db.scalar(select(ApplicantDocument).where(ApplicantDocument.id == document_id,
                                                   ApplicantDocument.applicant_id == applicant_id))
    if not row:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài liệu.")
    if user.role == "applicant" and row.status == "Đã xác nhận":
        raise HTTPException(status_code=409, detail="Tài liệu đã xác nhận không thể tự xóa.")
    db.delete(row)
    db.commit()


class ApplicantDocumentReview(BaseModel):
    status: str
    note: str = Field(default="", max_length=1000)


@document_router.patch("/admissions/applications/{applicant_id}/documents/{document_id}/review")
def review_applicant_document(applicant_id: str, document_id: str, data: ApplicantDocumentReview,
                              user: User = Depends(require_roles(*DOCUMENT_STAFF)), db: Session = Depends(get_db)):
    applicant = db.get(Applicant, applicant_id)
    row = db.scalar(select(ApplicantDocument).where(ApplicantDocument.id == document_id,
                                                   ApplicantDocument.applicant_id == applicant_id))
    if not applicant or not row:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ hoặc tài liệu.")
    if data.status not in DOCUMENT_REVIEW_STATES:
        raise HTTPException(status_code=422, detail="Trạng thái tài liệu không hợp lệ.")
    if data.status == "Cần bổ sung" and not data.note.strip():
        raise HTTPException(status_code=422, detail="Hãy nêu nội dung cần bổ sung.")
    row.status = data.status
    row.review_note = data.note.strip()
    row.reviewed_at = datetime.now(timezone.utc)
    row.reviewed_by = user.id
    account = db.scalar(select(User).where(User.email == applicant.email))
    if account:
        db.add(Notification(owner_id=account.id, title="Cập nhật tài liệu tuyển sinh",
                            message=f"{row.filename}: {row.status}" + (f" · {row.review_note}" if row.review_note else ""),
                            href="/admissions"))
    db.commit()
    db.refresh(row)
    return _document_public(row)
