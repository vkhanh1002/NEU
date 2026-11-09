from datetime import datetime
from typing import Literal
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator, model_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.database import get_db
from app.models import NewsArticle, UniversityEvent, User

router = APIRouter(prefix="/admin/content", tags=["Content administration"])


def _https_url(value: str, *, optional: bool = False) -> str:
    value = value.strip()
    if optional and not value:
        return value
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError("Chỉ chấp nhận liên kết HTTPS hợp lệ.")
    return value


class NewsInput(BaseModel):
    slug: str = Field(min_length=3, max_length=220, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    title: str = Field(min_length=8, max_length=240)
    category: str = Field(min_length=2, max_length=80)
    summary: str = Field(min_length=15, max_length=600)
    content: str = Field(min_length=30, max_length=50000)
    image_url: str = Field(default="", max_length=500)
    source_url: str = Field(default="", max_length=500)
    published_at: datetime | None = None
    status: Literal["draft", "published", "archived"] = "draft"

    @field_validator("source_url")
    @classmethod
    def validate_source_url(cls, value: str) -> str:
        return _https_url(value, optional=True)

    @field_validator("image_url")
    @classmethod
    def validate_image_url(cls, value: str) -> str:
        return _https_url(value, optional=True)

    @model_validator(mode="after")
    def published_news_has_source_and_date(self):
        if self.status == "published" and (not self.source_url or self.published_at is None):
            raise ValueError("Bài viết công khai cần liên kết nguồn và ngày đăng đã xác minh.")
        return self


class EventInput(BaseModel):
    title: str = Field(min_length=8, max_length=200)
    category: str = Field(min_length=2, max_length=80)
    summary: str = Field(min_length=15, max_length=500)
    location: str = Field(default="", max_length=180)
    starts_at: datetime
    ends_at: datetime
    is_all_day: bool = False
    source_url: str = Field(default="", max_length=500)
    status: Literal["draft", "published", "archived"] = "draft"

    @field_validator("source_url")
    @classmethod
    def validate_source_url(cls, value: str) -> str:
        return _https_url(value, optional=True)

    @model_validator(mode="after")
    def valid_event_window_and_source(self):
        if self.starts_at.tzinfo is None or self.ends_at.tzinfo is None:
            raise ValueError("Thời gian sự kiện cần có múi giờ.")
        if self.ends_at <= self.starts_at:
            raise ValueError("Thời gian kết thúc phải sau thời gian bắt đầu.")
        if self.status == "published" and not self.source_url:
            raise ValueError("Sự kiện công khai cần liên kết nguồn đã xác minh.")
        return self


def _news(row: NewsArticle) -> dict:
    return {"id": row.id, "slug": row.slug, "title": row.title, "category": row.category,
            "summary": row.summary, "content": row.content, "image_url": row.image_url,
            "source_url": row.source_url, "published_at": row.published_at, "status": row.status}


def _event(row: UniversityEvent) -> dict:
    return {"id": row.id, "title": row.title, "category": row.category, "summary": row.summary,
            "location": row.location, "starts_at": row.starts_at, "ends_at": row.ends_at,
            "is_all_day": row.is_all_day, "source_url": row.source_url, "status": row.status}


@router.get("/news")
def admin_news(_user: User = Depends(require_roles("super_admin")), db: Session = Depends(get_db)):
    rows = db.scalars(select(NewsArticle).order_by(NewsArticle.published_at.desc().nullslast(), NewsArticle.title)).all()
    return [_news(row) for row in rows]


@router.post("/news", status_code=201)
def create_news(data: NewsInput, _user: User = Depends(require_roles("super_admin")), db: Session = Depends(get_db)):
    if db.scalar(select(NewsArticle.id).where(NewsArticle.slug == data.slug)):
        raise HTTPException(status_code=409, detail="Đường dẫn bài viết đã tồn tại.")
    row = NewsArticle(**data.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return _news(row)


@router.patch("/news/{article_id}")
def update_news(article_id: str, data: NewsInput, _user: User = Depends(require_roles("super_admin")), db: Session = Depends(get_db)):
    row = db.get(NewsArticle, article_id)
    if not row:
        raise HTTPException(status_code=404, detail="Không tìm thấy bài viết.")
    duplicate = db.scalar(select(NewsArticle.id).where(NewsArticle.slug == data.slug, NewsArticle.id != row.id))
    if duplicate:
        raise HTTPException(status_code=409, detail="Đường dẫn bài viết đã tồn tại.")
    for key, value in data.model_dump().items():
        setattr(row, key, value)
    db.commit()
    db.refresh(row)
    return _news(row)


@router.delete("/news/{article_id}", status_code=204)
def delete_news(article_id: str, _user: User = Depends(require_roles("super_admin")), db: Session = Depends(get_db)):
    row = db.get(NewsArticle, article_id)
    if not row:
        raise HTTPException(status_code=404, detail="Không tìm thấy bài viết.")
    db.delete(row)
    db.commit()


@router.get("/events")
def admin_events(_user: User = Depends(require_roles("super_admin")), db: Session = Depends(get_db)):
    rows = db.scalars(select(UniversityEvent).order_by(UniversityEvent.starts_at.desc())).all()
    return [_event(row) for row in rows]


@router.post("/events", status_code=201)
def create_event(data: EventInput, _user: User = Depends(require_roles("super_admin")), db: Session = Depends(get_db)):
    row = UniversityEvent(**data.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return _event(row)


@router.patch("/events/{event_id}")
def update_event(event_id: str, data: EventInput, _user: User = Depends(require_roles("super_admin")), db: Session = Depends(get_db)):
    row = db.get(UniversityEvent, event_id)
    if not row:
        raise HTTPException(status_code=404, detail="Không tìm thấy sự kiện.")
    for key, value in data.model_dump().items():
        setattr(row, key, value)
    db.commit()
    db.refresh(row)
    return _event(row)


@router.delete("/events/{event_id}", status_code=204)
def delete_event(event_id: str, _user: User = Depends(require_roles("super_admin")), db: Session = Depends(get_db)):
    row = db.get(UniversityEvent, event_id)
    if not row:
        raise HTTPException(status_code=404, detail="Không tìm thấy sự kiện.")
    db.delete(row)
    db.commit()
