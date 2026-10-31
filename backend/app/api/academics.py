from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import current_user, require_roles
from app.core.database import get_db
from app.models import Applicant, Faculty, Major, Student, User
from app.schemas import ApplicantCreate, ApplicantPublic, ApplicantStatusUpdate, MajorPublic, StudentProfileUpdate, StudentPublic
from app.services.serializers import applicant_public, student_public

router = APIRouter(tags=["Admissions and profiles"])
STAFF = ("super_admin",)
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
def create_application(data: ApplicantCreate, db: Session = Depends(get_db)):
    major = db.get(Major, data.desired_major_id)
    if not major or major.admission_status != "Đang tuyển sinh":
        raise HTTPException(status_code=400, detail="Ngành không mở nhận hồ sơ trong dữ liệu hiện tại.")
    applicant = Applicant(**data.model_dump(), email=data.email.lower())
    db.add(applicant)
    db.commit()
    db.refresh(applicant)
    return applicant_public(db.scalar(select(Applicant).where(Applicant.id == applicant.id).options(joinedload(Applicant.major))))


@router.patch("/admissions/applications/{applicant_id}/status", response_model=ApplicantPublic)
def update_application_status(applicant_id: str, data: ApplicantStatusUpdate,
                              _user: User = Depends(require_roles("super_admin", "admission_staff")),
                              db: Session = Depends(get_db)):
    if data.status not in {"Mới tiếp nhận", "Đang xét duyệt", "Cần bổ sung", "Trúng tuyển", "Không trúng tuyển"}:
        raise HTTPException(status_code=422, detail="Trạng thái hồ sơ không hợp lệ.")
    applicant = db.scalar(select(Applicant).where(Applicant.id == applicant_id).options(joinedload(Applicant.major)))
    if not applicant:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ.")
    applicant.status = data.status
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
    count = db.scalar(select(func.count(Student.id))) or 0
    student = Student(
        applicant_id=applicant.id, student_number=f"STU{2026}{count + 1:04d}",
        full_name=applicant.full_name, email=applicant.email, phone=applicant.phone,
        date_of_birth=applicant.date_of_birth, address=applicant.address, major_id=applicant.desired_major_id,
        cohort="2026", enrollment_date=None, is_demo=False,
    )
    db.add(student)
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
    student = db.scalar(select(Student).where(Student.user_id == user.id).options(joinedload(Student.major)))
    if not student:
        raise HTTPException(status_code=404, detail="Tài khoản chưa được liên kết với hồ sơ sinh viên.")
    return student_public(student)


@router.patch("/profiles/me", response_model=StudentPublic)
def update_my_student_profile(data: StudentProfileUpdate, user: User = Depends(current_user), db: Session = Depends(get_db)):
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
