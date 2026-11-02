from sqlalchemy import func, select

from app.core.security import create_token, hash_password
from app.models import Applicant, Faculty, Personnel, Student, SupportTicket, User


def auth(user):
    return {"Authorization": f"Bearer {create_token(user.id)}"}


def test_super_admin_can_create_search_update_and_summarize_personnel(client, database):
    faculty = Faculty(name="Khoa Công nghệ")
    admin = User(email="people-admin@example.test", full_name="Quản trị", password_hash=hash_password("password"), role="super_admin")
    database.add_all([faculty, admin])
    database.commit()
    headers = auth(admin)

    lecturer = client.post("/api/v1/personnel", headers=headers, json={
        "code": "GV-TEST-001", "kind": "lecturer", "full_name": "Nguyễn Thị An", "email": "an@example.com",
        "phone": "0901234567", "faculty_id": faculty.id, "department": faculty.name,
        "specialty": "Khoa học máy tính", "position": "Giảng viên", "work_status": "Đang công tác",
    })
    employee = client.post("/api/v1/personnel", headers=headers, json={
        "code": "NV-TEST-001", "kind": "employee", "full_name": "Trần Văn Bình", "email": "binh@example.com",
        "department": "Phòng Đào tạo", "position": "Chuyên viên", "work_status": "Tạm nghỉ",
    })
    assert lecturer.status_code == employee.status_code == 201, (lecturer.text, employee.text)
    assert lecturer.json()["faculty_name"] == faculty.name
    found = client.get("/api/v1/personnel?kind=lecturer&q=Khoa+học+máy+tính&status=Đang+công+tác", headers=headers)
    assert [row["code"] for row in found.json()] == ["GV-TEST-001"]
    edited = client.patch(f"/api/v1/personnel/{lecturer.json()['id']}", headers=headers, json={"work_status": "Tạm nghỉ", "notes": "Đã cập nhật"})
    assert edited.status_code == 200
    assert edited.json()["notes"] == "Đã cập nhật"
    summary = client.get("/api/v1/personnel/dashboard", headers=headers).json()
    assert (summary["lecturers"], summary["employees"], summary["total"]) == (1, 1, 2)
    assert summary["active"] == 0 and summary["inactive"] == 2


def test_support_staff_can_search_assign_reply_and_access_attachments(client, database):
    student = User(email="ticket-owner@example.test", full_name="Sinh viên kiểm thử", password_hash=hash_password("password"), role="student")
    agent = User(email="support-agent@example.test", full_name="Nhân viên hỗ trợ", password_hash=hash_password("password"), role="support_staff")
    database.add_all([student, agent])
    database.commit()
    created = client.post("/api/v1/support/tickets", headers=auth(student), json={
        "category": "Hồ sơ sinh viên", "subject": "Xác nhận lớp hành chính", "description": "Nhờ xác nhận lớp hành chính của em.",
    })
    assert created.status_code == 201
    ticket_id = created.json()["id"]
    upload = client.post(f"/api/v1/support/tickets/{ticket_id}/attachments", headers=auth(student), files={"file": ("xac-nhan.txt", b"noi dung demo", "text/plain")})
    assert upload.status_code == 201
    attachment_id = upload.json()["attachments"][0]["id"]

    staff_headers = auth(agent)
    agents = client.get("/api/v1/support/agents", headers=staff_headers).json()
    assert any(row["id"] == agent.id for row in agents)
    result = client.get("/api/v1/support/tickets?q=Sinh+viên+kiểm+thử&category=Hồ+sơ+sinh+viên&status=Mới+tiếp+nhận", headers=staff_headers)
    assert [row["id"] for row in result.json()] == [ticket_id]
    assigned = client.patch(f"/api/v1/support/tickets/{ticket_id}/assignee", headers=staff_headers, json={"assignee_id": agent.id})
    assert assigned.status_code == 200 and assigned.json()["assignee_id"] == agent.id
    assert assigned.json()["status"] == "Đang xử lý"
    reply = client.post(f"/api/v1/support/tickets/{ticket_id}/messages", headers=staff_headers, json={"body": "Bộ phận hỗ trợ đã tiếp nhận."})
    assert reply.status_code == 200 and len(reply.json()["messages"]) == 1
    downloaded = client.get(f"/api/v1/support/tickets/{ticket_id}/attachments/{attachment_id}", headers=staff_headers)
    assert downloaded.status_code == 200 and downloaded.content == b"noi dung demo"
    dashboard = client.get("/api/v1/support/dashboard", headers=staff_headers).json()
    assert dashboard["total"] == 1
    assert next(row["count"] for row in dashboard["by_status"] if row["status"] == "Đang xử lý") == 1


def test_demo_seed_is_additive_and_idempotent(monkeypatch):
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app import seed

    engine = create_engine("sqlite://")
    TestingSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    monkeypatch.setattr(seed, "engine", engine)
    monkeypatch.setattr(seed, "SessionLocal", TestingSession)
    monkeypatch.setattr(seed, "enable_vector_extension", lambda: None)
    existing_admin = User(email="admin@study.edu.vn", full_name="Tên quản trị đã chỉnh sửa", password_hash=hash_password("original"), role="super_admin")
    # Create baseline tables before inserting a pre-existing account, just as an existing deployment would.
    seed.Base.metadata.create_all(bind=engine)
    with TestingSession() as db:
        db.add(existing_admin)
        db.commit()

    seed.seed_data()
    with TestingSession() as db:
        lecturer = db.scalar(select(Personnel).where(Personnel.code == "GV-NEU-001"))
        lecturer.full_name = "Tên giảng viên đã chỉnh sửa"
        db.commit()
    seed.seed_data()
    with TestingSession() as db:
        assert db.scalar(select(func.count(Student.id))) == 20
        assert db.scalar(select(func.count(Personnel.id))) == 15
        assert db.scalar(select(func.count(SupportTicket.id))) == 26
        assert db.scalar(select(func.count(Applicant.id))) == 25
        saved_admin = db.scalar(select(User).where(User.email == "admin@neu.local"))
        assert saved_admin.full_name == "Tên quản trị đã chỉnh sửa"
        assert saved_admin.password_hash == existing_admin.password_hash
        saved_lecturer = db.scalar(select(Personnel).where(Personnel.code == "GV-NEU-001"))
        assert saved_lecturer.full_name == "Tên giảng viên đã chỉnh sửa"
    engine.dispose()
