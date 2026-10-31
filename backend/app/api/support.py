from uuid import uuid4

from urllib.parse import quote

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import Response
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import current_user, require_roles
from app.core.database import get_db
from app.models import FAQ, Notification, SupportTicket, TicketAttachment, TicketMessage, User
from app.schemas import FAQAdminPublic, FAQCreate, FAQPublic, TicketAssign, TicketCreate, TicketPublic, TicketRating, TicketReply, TicketStatusUpdate
from app.services.serializers import ticket_public

router = APIRouter(tags=["Student support"])
SUPPORT_ROLES = ("super_admin", "support_staff")
TICKET_STATES = {"Mới tiếp nhận", "Đang xử lý", "Chờ bổ sung thông tin", "Đã giải quyết", "Đã đóng"}


@router.get("/support/faqs", response_model=list[FAQPublic])
def list_faqs(db: Session = Depends(get_db)):
    return db.scalars(select(FAQ).where(FAQ.is_published.is_(True)).order_by(FAQ.category, FAQ.question)).all()


@router.get("/support/tickets", response_model=list[TicketPublic])
def list_tickets(q: str | None = None, category: str | None = None, status: str | None = None,
                 user: User = Depends(current_user), db: Session = Depends(get_db)):
    query = select(SupportTicket).options(joinedload(SupportTicket.owner), joinedload(SupportTicket.messages), joinedload(SupportTicket.attachments)).order_by(SupportTicket.created_at.desc())
    if user.role not in SUPPORT_ROLES:
        query = query.where(SupportTicket.owner_id == user.id)
    if category:
        query = query.where(SupportTicket.category == category)
    if status:
        query = query.where(SupportTicket.status == status)
    if q and q.strip():
        pattern = f"%{q.strip()}%"
        query = query.join(SupportTicket.owner).where(or_(SupportTicket.code.ilike(pattern), SupportTicket.subject.ilike(pattern),
                                                           SupportTicket.description.ilike(pattern), User.full_name.ilike(pattern)))
    return [ticket_public(row) for row in db.scalars(query).unique().all()]


@router.get("/support/agents")
def list_support_agents(_user: User = Depends(require_roles(*SUPPORT_ROLES)), db: Session = Depends(get_db)):
    agents = db.scalars(select(User).where(User.role.in_(SUPPORT_ROLES), User.is_active.is_(True)).order_by(User.full_name)).all()
    return [{"id": row.id, "full_name": row.full_name, "email": row.email} for row in agents]


@router.get("/support/dashboard")
def support_dashboard(_user: User = Depends(require_roles(*SUPPORT_ROLES)), db: Session = Depends(get_db)):
    counts = {status: db.scalar(select(func.count(SupportTicket.id)).where(SupportTicket.status == status)) or 0 for status in TICKET_STATES}
    total = sum(counts.values())
    resolved = counts["Đã giải quyết"] + counts["Đã đóng"]
    recent = db.scalars(select(SupportTicket).options(joinedload(SupportTicket.owner)).order_by(SupportTicket.created_at.desc()).limit(5)).all()
    return {"total": total, "by_status": [{"status": key, "count": value} for key, value in counts.items()],
            "success_rate": round(resolved * 100 / total, 1) if total else 0,
            "recent": [{"id": row.id, "code": row.code, "subject": row.subject, "owner_name": row.owner.full_name,
                        "status": row.status, "category": row.category, "created_at": row.created_at} for row in recent]}


@router.post("/support/tickets", response_model=TicketPublic, status_code=201)
def create_ticket(data: TicketCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    ticket = SupportTicket(code=f"ST-{uuid4().hex[:8].upper()}", owner_id=user.id, **data.model_dump())
    db.add(ticket)
    db.commit()
    ticket = db.scalar(select(SupportTicket).where(SupportTicket.id == ticket.id).options(joinedload(SupportTicket.owner), joinedload(SupportTicket.messages)))
    return ticket_public(ticket)


@router.post("/support/tickets/{ticket_id}/messages", response_model=TicketPublic)
def reply_ticket(ticket_id: str, data: TicketReply, user: User = Depends(current_user), db: Session = Depends(get_db)):
    ticket = db.scalar(select(SupportTicket).where(SupportTicket.id == ticket_id).options(joinedload(SupportTicket.owner), joinedload(SupportTicket.messages)))
    if not ticket:
        raise HTTPException(status_code=404, detail="Không tìm thấy yêu cầu hỗ trợ.")
    if ticket.owner_id != user.id and user.role not in SUPPORT_ROLES:
        raise HTTPException(status_code=403, detail="Bạn không có quyền truy cập yêu cầu này.")
    ticket.messages.append(TicketMessage(author_id=user.id, body=data.body))
    if user.id != ticket.owner_id:
        db.add(Notification(owner_id=ticket.owner_id, title="Phản hồi yêu cầu hỗ trợ",
                            message=f"Bộ phận hỗ trợ đã phản hồi {ticket.code} · {ticket.subject}.", href="/support"))
    db.commit()
    ticket = db.scalar(select(SupportTicket).where(SupportTicket.id == ticket_id).options(joinedload(SupportTicket.owner), joinedload(SupportTicket.messages)))
    return ticket_public(ticket)


@router.post("/support/tickets/{ticket_id}/attachments", response_model=TicketPublic, status_code=201)
async def upload_ticket_attachment(ticket_id: str, file: UploadFile = File(...), user: User = Depends(current_user), db: Session = Depends(get_db)):
    ticket = db.scalar(select(SupportTicket).where(SupportTicket.id == ticket_id).options(joinedload(SupportTicket.owner), joinedload(SupportTicket.messages), joinedload(SupportTicket.attachments)))
    if not ticket:
        raise HTTPException(status_code=404, detail="Không tìm thấy yêu cầu hỗ trợ.")
    if ticket.owner_id != user.id and user.role not in SUPPORT_ROLES:
        raise HTTPException(status_code=403, detail="Bạn không có quyền truy cập yêu cầu này.")
    filename = (file.filename or "attachment").replace("\\", "/").split("/")[-1]
    if not filename.lower().endswith((".pdf", ".docx", ".txt", ".png", ".jpg", ".jpeg")):
        raise HTTPException(status_code=415, detail="Chỉ chấp nhận PDF, DOCX, TXT, PNG hoặc JPG.")
    content = await file.read(10 * 1024 * 1024 + 1)
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Mỗi tệp đính kèm tối đa 10 MB.")
    ticket.attachments.append(TicketAttachment(uploaded_by=user.id, filename=filename,
                                                media_type=file.content_type or "application/octet-stream",
                                                size_bytes=len(content), content=content))
    db.commit()
    ticket = db.scalar(select(SupportTicket).where(SupportTicket.id == ticket_id).options(joinedload(SupportTicket.owner), joinedload(SupportTicket.messages), joinedload(SupportTicket.attachments)))
    return ticket_public(ticket)


@router.get("/support/tickets/{ticket_id}/attachments/{attachment_id}")
def download_ticket_attachment(ticket_id: str, attachment_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    ticket = db.get(SupportTicket, ticket_id)
    attachment = db.scalar(select(TicketAttachment).where(TicketAttachment.id == attachment_id, TicketAttachment.ticket_id == ticket_id))
    if not ticket or not attachment:
        raise HTTPException(status_code=404, detail="Không tìm thấy tệp đính kèm.")
    if ticket.owner_id != user.id and user.role not in SUPPORT_ROLES:
        raise HTTPException(status_code=403, detail="Bạn không có quyền tải tệp này.")
    safe_name = quote(attachment.filename)
    return Response(content=attachment.content, media_type=attachment.media_type,
                    headers={"Content-Disposition": f"attachment; filename*=UTF-8''{safe_name}"})


@router.patch("/support/tickets/{ticket_id}/status", response_model=TicketPublic)
def update_ticket_status(ticket_id: str, data: TicketStatusUpdate,
                         user: User = Depends(require_roles(*SUPPORT_ROLES)), db: Session = Depends(get_db)):
    if data.status not in TICKET_STATES:
        raise HTTPException(status_code=422, detail="Trạng thái không hợp lệ.")
    ticket = db.scalar(select(SupportTicket).where(SupportTicket.id == ticket_id).options(joinedload(SupportTicket.owner), joinedload(SupportTicket.messages)))
    if not ticket:
        raise HTTPException(status_code=404, detail="Không tìm thấy yêu cầu hỗ trợ.")
    ticket.status = data.status
    if not ticket.assignee_id:
        ticket.assignee_id = user.id
    db.add(Notification(owner_id=ticket.owner_id, title="Cập nhật yêu cầu hỗ trợ",
                        message=f"{ticket.code} · {ticket.subject}: {ticket.status}", href="/support"))
    db.commit()
    return ticket_public(ticket)


@router.patch("/support/tickets/{ticket_id}/assignee", response_model=TicketPublic)
def assign_ticket(ticket_id: str, data: TicketAssign,
                  user: User = Depends(require_roles(*SUPPORT_ROLES)), db: Session = Depends(get_db)):
    ticket = db.scalar(select(SupportTicket).where(SupportTicket.id == ticket_id).options(joinedload(SupportTicket.owner), joinedload(SupportTicket.messages), joinedload(SupportTicket.attachments)))
    if not ticket:
        raise HTTPException(status_code=404, detail="Không tìm thấy yêu cầu hỗ trợ.")
    if data.assignee_id:
        assignee = db.get(User, data.assignee_id)
        if not assignee or assignee.role not in SUPPORT_ROLES or not assignee.is_active:
            raise HTTPException(status_code=422, detail="Người phụ trách phải là nhân viên hỗ trợ đang hoạt động.")
    ticket.assignee_id = data.assignee_id
    if data.assignee_id and ticket.status == "Mới tiếp nhận":
        ticket.status = "Đang xử lý"
    if ticket.assignee_id:
        db.add(Notification(owner_id=ticket.owner_id, title="Yêu cầu đã được phân công",
                            message=f"{ticket.code} · {ticket.subject} đang được nhân viên hỗ trợ xử lý.", href="/support"))
    db.commit()
    return ticket_public(ticket)


@router.post("/support/tickets/{ticket_id}/rating", response_model=TicketPublic)
def rate_ticket(ticket_id: str, data: TicketRating, user: User = Depends(current_user), db: Session = Depends(get_db)):
    ticket = db.scalar(select(SupportTicket).where(SupportTicket.id == ticket_id).options(joinedload(SupportTicket.owner), joinedload(SupportTicket.messages)))
    if not ticket:
        raise HTTPException(status_code=404, detail="Không tìm thấy yêu cầu hỗ trợ.")
    if ticket.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Bạn không có quyền đánh giá yêu cầu này.")
    if ticket.status not in {"Đã giải quyết", "Đã đóng"}:
        raise HTTPException(status_code=409, detail="Chỉ đánh giá được yêu cầu đã giải quyết hoặc đã đóng.")
    ticket.satisfaction_rating = data.rating
    ticket.satisfaction_feedback = data.feedback
    db.commit()
    return ticket_public(ticket)


@router.get("/admin/faqs", response_model=list[FAQAdminPublic])
def admin_list_faqs(_user: User = Depends(require_roles("super_admin")), db: Session = Depends(get_db)):
    return db.scalars(select(FAQ).order_by(FAQ.category, FAQ.question)).all()


@router.post("/admin/faqs", response_model=FAQAdminPublic, status_code=201)
def create_faq(data: FAQCreate, _user: User = Depends(require_roles("super_admin")), db: Session = Depends(get_db)):
    faq = FAQ(**data.model_dump(), is_published=True)
    db.add(faq)
    db.commit()
    db.refresh(faq)
    return faq


@router.delete("/admin/faqs/{faq_id}", status_code=204)
def delete_faq(faq_id: str, _user: User = Depends(require_roles("super_admin")), db: Session = Depends(get_db)):
    faq = db.get(FAQ, faq_id)
    if not faq:
        raise HTTPException(status_code=404, detail="Không tìm thấy FAQ.")
    db.delete(faq)
    db.commit()
