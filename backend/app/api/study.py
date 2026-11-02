from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.core.database import get_db
from app.models import StudyTask, User
from app.schemas import StudySummary, StudyTaskCreate, StudyTaskPublic, StudyTaskUpdate

router = APIRouter(tags=["Study Planner & Tasks"])


@router.get("/study/tasks", response_model=list[StudyTaskPublic])
def list_tasks(
    status: str | None = None,
    task_type: str | None = None,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    query = select(StudyTask).where(StudyTask.user_id == user.id)
    if status:
        query = query.where(StudyTask.status == status)
    if task_type:
        query = query.where(StudyTask.task_type == task_type)
    query = query.order_by(StudyTask.due_date.asc())
    return db.scalars(query).all()


@router.get("/study/summary", response_model=StudySummary)
def get_study_summary(
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    all_tasks = db.scalars(
        select(StudyTask)
        .where(StudyTask.user_id == user.id)
        .order_by(StudyTask.due_date.asc())
    ).all()

    now = datetime.now(timezone.utc)
    pending = [t for t in all_tasks if t.status != "completed"]
    upcoming_deadlines = [t for t in pending if t.task_type in ("assignment", "project", "quiz")]
    upcoming_exams = [t for t in pending if t.task_type == "exam"]

    return StudySummary(
        total_tasks=len(all_tasks),
        pending_tasks=len(pending),
        upcoming_deadlines=len(upcoming_deadlines),
        upcoming_exams=len(upcoming_exams),
        tasks=all_tasks[:10],
    )


@router.post("/study/tasks", response_model=StudyTaskPublic)
def create_task(
    payload: StudyTaskCreate,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    task = StudyTask(
        user_id=user.id,
        title=payload.title.strip(),
        course_name=payload.course_name.strip(),
        task_type=payload.task_type,
        due_date=payload.due_date,
        priority=payload.priority,
        notes=payload.notes.strip(),
        status="pending",
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.patch("/study/tasks/{task_id}", response_model=StudyTaskPublic)
def update_task(
    task_id: str,
    payload: StudyTaskUpdate,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    task = db.scalar(
        select(StudyTask).where(StudyTask.id == task_id, StudyTask.user_id == user.id)
    )
    if not task:
        raise HTTPException(status_code=404, detail="Không tìm thấy mục học tập.")

    for field, val in payload.model_dump(exclude_unset=True).items():
        if val is not None:
            setattr(task, field, val)

    db.commit()
    db.refresh(task)
    return task


@router.delete("/study/tasks/{task_id}")
def delete_task(
    task_id: str,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    task = db.scalar(
        select(StudyTask).where(StudyTask.id == task_id, StudyTask.user_id == user.id)
    )
    if not task:
        raise HTTPException(status_code=404, detail="Không tìm thấy mục học tập.")

    db.delete(task)
    db.commit()
    return {"ok": True, "message": "Đã xóa mục học tập."}
