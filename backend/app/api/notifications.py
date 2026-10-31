from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.core.database import get_db
from app.models import Notification, User
from app.schemas import NotificationPublic

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("")
def list_notifications(user: User = Depends(current_user), db: Session = Depends(get_db)):
    rows = db.scalars(select(Notification).where(Notification.owner_id == user.id).order_by(Notification.created_at.desc()).limit(20)).all()
    unread = db.scalar(select(func.count(Notification.id)).where(Notification.owner_id == user.id, Notification.read_at.is_(None))) or 0
    return {"items": [NotificationPublic.model_validate(row).model_dump(mode="json") for row in rows], "unread_count": unread}


@router.patch("/{notification_id}/read", response_model=NotificationPublic)
def mark_read(notification_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    notification = db.scalar(select(Notification).where(Notification.id == notification_id, Notification.owner_id == user.id))
    if not notification:
        raise HTTPException(status_code=404, detail="Không tìm thấy thông báo.")
    notification.read_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(notification)
    return notification
