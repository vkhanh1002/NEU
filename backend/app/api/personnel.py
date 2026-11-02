from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import require_roles
from app.core.database import get_db
from app.models import Faculty, Personnel, User
from app.schemas import PersonnelCreate, PersonnelPublic, PersonnelUpdate
from app.services.serializers import personnel_public

router = APIRouter(prefix="/personnel", tags=["Personnel"])
ADMIN = ("super_admin", "hr_staff")
ACTIVE = "Đang công tác"


def _base_query():
    return select(Personnel).options(joinedload(Personnel.faculty))


@router.get("", response_model=list[PersonnelPublic])
def list_personnel(kind: str | None = None, q: str | None = None, status: str | None = None,
                   department: str | None = None, faculty_id: str | None = None,
                   _user: User = Depends(require_roles(*ADMIN)), db: Session = Depends(get_db)):
    query = _base_query()
    if kind in {"lecturer", "employee"}:
        query = query.where(Personnel.kind == kind)
    if status:
        query = query.where(Personnel.work_status == status)
    if department:
        query = query.where(Personnel.department.ilike(f"%{department}%"))
    if faculty_id:
        query = query.where(Personnel.faculty_id == faculty_id)
    if q and q.strip():
        pattern = f"%{q.strip()}%"
        query = query.outerjoin(Faculty, Personnel.faculty_id == Faculty.id).where(
            or_(Personnel.code.ilike(pattern), Personnel.full_name.ilike(pattern), Personnel.email.ilike(pattern),
                Personnel.specialty.ilike(pattern), Personnel.department.ilike(pattern), Faculty.name.ilike(pattern))
        )
    rows = db.scalars(query.order_by(Personnel.kind, Personnel.code)).unique().all()
    return [personnel_public(row) for row in rows]


@router.get("/dashboard")
def personnel_dashboard(_user: User = Depends(require_roles(*ADMIN)), db: Session = Depends(get_db)):
    totals = {kind: db.scalar(select(func.count(Personnel.id)).where(Personnel.kind == kind)) or 0
              for kind in ("lecturer", "employee")}
    by_status = db.execute(select(Personnel.work_status, func.count(Personnel.id)).group_by(Personnel.work_status)).all()
    by_unit = db.execute(select(Personnel.department, func.count(Personnel.id)).group_by(Personnel.department).order_by(func.count(Personnel.id).desc())).all()
    active = db.scalar(select(func.count(Personnel.id)).where(Personnel.work_status == ACTIVE)) or 0
    return {"lecturers": totals["lecturer"], "employees": totals["employee"], "total": sum(totals.values()),
            "active": active, "inactive": sum(totals.values()) - active,
            "by_status": [{"name": name, "count": count} for name, count in by_status],
            "by_unit": [{"name": name or "Chưa phân đơn vị", "count": count} for name, count in by_unit]}


@router.post("", response_model=PersonnelPublic, status_code=201)
def create_personnel(data: PersonnelCreate, _user: User = Depends(require_roles(*ADMIN)), db: Session = Depends(get_db)):
    if db.scalar(select(Personnel.id).where(Personnel.code == data.code)):
        raise HTTPException(status_code=409, detail="Mã hồ sơ nhân sự đã tồn tại.")
    if db.scalar(select(Personnel.id).where(Personnel.email == data.email.lower())):
        raise HTTPException(status_code=409, detail="Email nhân sự đã tồn tại.")
    if data.faculty_id and not db.get(Faculty, data.faculty_id):
        raise HTTPException(status_code=422, detail="Không tìm thấy khoa đã chọn.")
    row = Personnel(**data.model_dump(exclude={"email"}), email=data.email.lower())
    db.add(row)
    db.commit()
    row = db.scalar(_base_query().where(Personnel.id == row.id))
    return personnel_public(row)


@router.get("/{personnel_id}", response_model=PersonnelPublic)
def get_personnel(personnel_id: str, _user: User = Depends(require_roles(*ADMIN)), db: Session = Depends(get_db)):
    row = db.scalar(_base_query().where(Personnel.id == personnel_id))
    if not row:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ nhân sự.")
    return personnel_public(row)


@router.patch("/{personnel_id}", response_model=PersonnelPublic)
def update_personnel(personnel_id: str, data: PersonnelUpdate,
                     _user: User = Depends(require_roles(*ADMIN)), db: Session = Depends(get_db)):
    row = db.get(Personnel, personnel_id)
    if not row:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ nhân sự.")
    updates = data.model_dump(exclude_unset=True)
    email = updates.get("email")
    if email and db.scalar(select(Personnel.id).where(Personnel.email == email.lower(), Personnel.id != row.id)):
        raise HTTPException(status_code=409, detail="Email nhân sự đã được sử dụng.")
    if updates.get("faculty_id") and not db.get(Faculty, updates["faculty_id"]):
        raise HTTPException(status_code=422, detail="Không tìm thấy khoa đã chọn.")
    if email:
        updates["email"] = email.lower()
    for field, value in updates.items():
        setattr(row, field, value)
    db.commit()
    row = db.scalar(_base_query().where(Personnel.id == personnel_id))
    return personnel_public(row)
