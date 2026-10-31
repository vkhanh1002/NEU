from app.ai.rag import chunks_for, cosine_similarity, extract_document, lexical_score
import pytest
import asyncio

from app.ai.rag import generate_answer, retrieve_context
from app.core.security import create_token, decode_token, hash_password, verify_password
from app.models import Applicant, FAQ, Faculty, Major, Student, SupportTicket, User


def test_password_hashing_and_token_types():
    hashed = hash_password("secure-demo-password")
    assert hashed != "secure-demo-password"
    assert verify_password("secure-demo-password", hashed)
    assert not verify_password("wrong-password", hashed)
    token = create_token("user-123")
    assert decode_token(token) == "user-123"
    with pytest.raises(Exception):
        decode_token(token, "refresh")


def test_chunking_and_retrieval_helpers():
    text = "Thông tin tuyển sinh và học phí. " * 100
    chunks = chunks_for(text, size=200, overlap=30)
    assert len(chunks) > 1
    assert all(chunks)
    assert lexical_score("học phí", "Học phí tham khảo ngành công nghệ") > 0
    assert cosine_similarity([1, 0], [0.5, 0.5]) > 0


def test_extract_markdown_knowledge_document():
    text = "---\ntitle: Tài liệu tiếng Việt\n---\n# Học phí\n\nNội dung mẫu."
    expected = "Tài liệu: Tài liệu tiếng Việt\n\n# Học phí\n\nNội dung mẫu."
    assert extract_document("guide.md", text.encode("utf-8")) == expected
    assert extract_document("guide.markdown", text.encode("utf-8")) == expected


def test_role_protected_route_rejects_anonymous_request(client):
    response = client.get("/api/v1/admissions/applications")
    assert response.status_code == 401


def test_dashboard_returns_demo_analytics(client):
    response = client.get("/api/v1/dashboard")
    assert response.status_code == 200
    body = response.json()
    assert body["demo_data"] is True
    assert len(body["admissions_by_month"]) == 12


def test_login_and_role_protected_application_conversion(client, database):
    faculty = Faculty(name="Khoa mẫu")
    database.add(faculty)
    database.flush()
    major = Major(code="999999", name="Ngành mẫu", faculty_id=faculty.id, description="Mẫu", duration_years=4,
                  tuition_per_year_vnd=1, admission_quota=10, admission_status="Đang tuyển sinh", is_demo=True)
    admin = User(email="admin@example.com", full_name="Admin", password_hash=hash_password("correct-password"), role="super_admin")
    database.add_all([major, admin])
    database.flush()
    applicant = Applicant(email="candidate@example.com", full_name="Ứng viên Mẫu", desired_major_id=major.id, status="Đang xét duyệt")
    database.add(applicant)
    database.commit()

    login = client.post("/api/v1/auth/login", json={"email": admin.email, "password": "correct-password"})
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    assert client.patch(f"/api/v1/admissions/applications/{applicant.id}/status", json={"status": "Trúng tuyển"}, headers=headers).status_code == 200
    promoted = client.post(f"/api/v1/admissions/applications/{applicant.id}/promote", headers=headers)
    assert promoted.status_code == 200
    assert promoted.json()["email"] == "candidate@example.com"
    assert promoted.json()["major_id"] == major.id
    assert client.post(f"/api/v1/admissions/applications/{applicant.id}/promote", headers=headers).json()["id"] == promoted.json()["id"]


def test_student_scope_prevents_cross_account_profile_and_ticket_access(client, database):
    faculty = Faculty(name="Khoa quyền riêng tư")
    database.add(faculty)
    database.flush()
    major = Major(code="900001", name="Ngành", faculty_id=faculty.id, description="", duration_years=4,
                  tuition_per_year_vnd=1, admission_quota=1, is_demo=True)
    owner = User(email="owner@test.local", full_name="Sinh viên A", password_hash=hash_password("password-A"), role="student")
    other = User(email="other@test.local", full_name="Sinh viên B", password_hash=hash_password("password-B"), role="student")
    database.add_all([major, owner, other])
    database.flush()
    database.add_all([
        Student(user_id=owner.id, student_number="STU-A", full_name=owner.full_name, email=owner.email, major_id=major.id),
        Student(user_id=other.id, student_number="STU-B", full_name=other.full_name, email=other.email, major_id=major.id),
    ])
    private_ticket = SupportTicket(code="ST-PRIVATE1", owner_id=other.id, category="Khác", subject="Riêng tư", description="Nội dung riêng tư", priority="Thấp")
    database.add(private_ticket)
    database.commit()

    token = create_token(owner.id)
    headers = {"Authorization": f"Bearer {token}"}
    profile_rows = client.get("/api/v1/profiles/students", headers=headers)
    assert profile_rows.status_code == 200
    assert [row["student_number"] for row in profile_rows.json()] == ["STU-A"]
    updated_profile = client.patch("/api/v1/profiles/me", headers=headers, json={"phone": "0901234567"})
    assert updated_profile.status_code == 200
    assert updated_profile.json()["phone"] == "0901234567"
    assert client.patch(f"/api/v1/profiles/students/{updated_profile.json()['id']}", headers={"Authorization": f"Bearer {create_token(other.id)}"}, json={"phone": "000"}).status_code == 403
    denied = client.post(f"/api/v1/support/tickets/{private_ticket.id}/messages", json={"body": "Xem thử"}, headers=headers)
    assert denied.status_code == 403


def test_student_can_create_and_follow_own_support_ticket(client, database):
    user = User(email="student@example.com", full_name="Sinh viên", password_hash=hash_password("password"), role="student")
    database.add(user)
    database.commit()
    headers = {"Authorization": f"Bearer {create_token(user.id)}"}
    created = client.post("/api/v1/support/tickets", headers=headers, json={
        "category": "Đào tạo", "subject": "Xác nhận lịch học", "description": "Nhờ hướng dẫn cách xác nhận lịch học của em.", "priority": "Bình thường",
    })
    assert created.status_code == 201
    ticket_id = created.json()["id"]
    reply = client.post(f"/api/v1/support/tickets/{ticket_id}/messages", headers=headers, json={"body": "Em xin bổ sung thông tin."})
    assert reply.status_code == 200
    assert len(reply.json()["messages"]) == 1
    support = User(email="support@example.com", full_name="Nhân viên hỗ trợ", password_hash=hash_password("password"), role="support_staff")
    database.add(support)
    database.commit()
    staff_headers = {"Authorization": f"Bearer {create_token(support.id)}"}
    status_update = client.patch(f"/api/v1/support/tickets/{ticket_id}/status", headers=staff_headers, json={"status": "Đã giải quyết"})
    assert status_update.status_code == 200
    notification_response = client.get("/api/v1/notifications", headers=headers)
    assert notification_response.json()["unread_count"] == 1
    notification_id = notification_response.json()["items"][0]["id"]
    assert client.patch(f"/api/v1/notifications/{notification_id}/read", headers=staff_headers).status_code == 404
    rated = client.post(f"/api/v1/support/tickets/{ticket_id}/rating", headers=headers, json={"rating": 5, "feedback": "Rõ ràng, cảm ơn."})
    assert rated.status_code == 200
    assert rated.json()["satisfaction_rating"] == 5


def test_chat_history_is_private_between_users(client, database):
    first = User(email="first@example.com", full_name="First", password_hash=hash_password("password"), role="student")
    second = User(email="second@example.com", full_name="Second", password_hash=hash_password("password"), role="student")
    database.add_all([first, second])
    database.commit()
    first_headers = {"Authorization": f"Bearer {create_token(first.id)}"}
    second_headers = {"Authorization": f"Bearer {create_token(second.id)}"}
    conversation = client.post("/api/v1/assistant/conversations", headers=first_headers, json={"title": "Riêng tư"}).json()
    assert client.get(f"/api/v1/assistant/conversations/{conversation['id']}", headers=second_headers).status_code == 404
    assert client.patch(f"/api/v1/assistant/conversations/{conversation['id']}", headers=second_headers, json={"title": "Tôi đã vào đây"}).status_code == 404


def test_rag_retrieves_faq_and_demo_answer_is_grounded(database, monkeypatch):
    from app.core.config import settings
    monkeypatch.setattr(settings, "ai_provider", "gemini")
    monkeypatch.setattr(settings, "gemini_api_key", None)
    monkeypatch.setattr(settings, "groq_api_key", None)
    database.add(FAQ(question="Điều kiện đăng ký xét tuyển là gì?", answer="Thí sinh xem hướng dẫn của đợt tuyển sinh và chuẩn bị thông tin theo yêu cầu.", category="Tuyển sinh"))
    database.commit()
    sources = asyncio.run(retrieve_context(database, "Điều kiện đăng ký xét tuyển là gì?"))
    assert sources
    assert sources[0]["source_type"] == "FAQ"
    answer = asyncio.run(generate_answer("Điều kiện đăng ký xét tuyển là gì?", sources, []))
    assert answer.mode == "retrieval_only"
    assert "hướng dẫn của đợt tuyển sinh" in answer.content


def test_chat_message_is_saved_with_retrieval_sources(client, database, monkeypatch):
    from app.core.config import settings
    monkeypatch.setattr(settings, "ai_provider", "gemini")
    monkeypatch.setattr(settings, "gemini_api_key", None)
    monkeypatch.setattr(settings, "groq_api_key", None)
    user = User(email="assistant@example.com", full_name="Sinh viên", password_hash=hash_password("password"), role="student")
    database.add(user)
    database.add(FAQ(question="Làm thế nào để gửi yêu cầu hỗ trợ?", answer="Mở Trung tâm hỗ trợ, chọn nhóm vấn đề và gửi mô tả.", category="Hỗ trợ"))
    database.commit()
    headers = {"Authorization": f"Bearer {create_token(user.id)}"}
    conversation = client.post("/api/v1/assistant/conversations", headers=headers, json={}).json()
    response = client.post(f"/api/v1/assistant/conversations/{conversation['id']}/messages", headers=headers,
                           json={"message": "Làm thế nào để gửi yêu cầu hỗ trợ?"})
    assert response.status_code == 200
    assert response.json()["demo_mode"] is True
    assert response.json()["message"]["sources"][0]["source_type"] == "FAQ"
    history = client.get(f"/api/v1/assistant/conversations/{conversation['id']}", headers=headers).json()["messages"]
    assert [message["role"] for message in history] == ["user", "assistant"]


def test_streaming_chat_saves_only_complete_answer_and_sources(client, database, monkeypatch):
    from app.ai.providers import ProviderStreamEvent, provider_manager
    from app.core.config import settings
    monkeypatch.setattr(settings, "ai_provider", "groq")
    monkeypatch.setattr(settings, "groq_api_key", "test-key")
    monkeypatch.setattr(settings, "gemini_api_key", None)
    async def fake_retrieval(_db, _question):
        return [{"title": "Hướng dẫn tuyển sinh", "excerpt": "Chuẩn bị hồ sơ theo hướng dẫn tuyển sinh.",
                 "source_type": "Tài liệu", "score": 1.0}]
    async def fake_stream(_system, _history, _question, *, allow_fallback=True, on_status=None, budget_seconds=None):
        if on_status:
            on_status({"state": "requesting", "provider": "groq", "attempt": 1, "max_attempts": 2})
        yield ProviderStreamEvent("token", text="Chuẩn bị ", provider="groq", model="openai/gpt-oss-20b")
        yield ProviderStreamEvent("token", text="hồ sơ tuyển sinh.", provider="groq", model="openai/gpt-oss-20b")
        yield ProviderStreamEvent("complete", provider="groq", model="openai/gpt-oss-20b",
                                  metrics={"provider_seconds": 0.2, "ttft_seconds": 0.1, "generation_seconds": 0.1,
                                           "input_tokens": 20, "output_tokens": 6, "retry_count": 0, "fallback_count": 0})
    monkeypatch.setattr("app.api.assistant.retrieve_context", fake_retrieval)
    monkeypatch.setattr(provider_manager, "stream", fake_stream)
    user = User(email="stream@example.com", full_name="Sinh viên", password_hash=hash_password("password"), role="student")
    database.add(user)
    database.commit()
    headers = {"Authorization": f"Bearer {create_token(user.id)}"}
    conversation = client.post("/api/v1/assistant/conversations", headers=headers, json={}).json()
    response = client.post(f"/api/v1/assistant/conversations/{conversation['id']}/messages/stream",
                           headers=headers, json={"message": "Hồ sơ tuyển sinh cần gì?"})
    assert response.status_code == 200 and "event: token" in response.text and "event: complete" in response.text
    assert "openai/gpt-oss-20b" in response.text
    history = client.get(f"/api/v1/assistant/conversations/{conversation['id']}", headers=headers).json()["messages"]
    assert [message["role"] for message in history] == ["user", "assistant"]
    assert history[-1]["content"] == "Chuẩn bị hồ sơ tuyển sinh."
    assert history[-1]["sources"][0]["title"] == "Hướng dẫn tuyển sinh"


def test_stream_failure_does_not_save_partial_answer(client, database, monkeypatch):
    from app.ai.providers import ProviderError, ProviderStreamEvent, provider_manager
    from app.core.config import settings
    monkeypatch.setattr(settings, "ai_provider", "groq")
    monkeypatch.setattr(settings, "groq_api_key", "test-key")
    async def fake_retrieval(_db, _question): return []
    async def fake_stream(*_args, **_kwargs):
        yield ProviderStreamEvent("token", text="Phần chưa hoàn tất", provider="groq", model="openai/gpt-oss-20b")
        raise ProviderError("groq", 503, "UNAVAILABLE", partial_output=True)
    monkeypatch.setattr("app.api.assistant.retrieve_context", fake_retrieval)
    monkeypatch.setattr(provider_manager, "stream", fake_stream)
    user = User(email="stream-failure@example.com", full_name="Sinh viên", password_hash=hash_password("password"), role="student")
    database.add(user)
    database.commit()
    headers = {"Authorization": f"Bearer {create_token(user.id)}"}
    conversation = client.post("/api/v1/assistant/conversations", headers=headers, json={}).json()
    response = client.post(f"/api/v1/assistant/conversations/{conversation['id']}/messages/stream",
                           headers=headers, json={"message": "Hỏi thử"})
    assert response.status_code == 200 and "event: error" in response.text
    history = client.get(f"/api/v1/assistant/conversations/{conversation['id']}", headers=headers).json()["messages"]
    assert [message["role"] for message in history] == ["user"]


def test_ai_personal_lookup_only_includes_current_students_record(client, database, monkeypatch):
    from app.core.config import settings
    async def forbidden_retrieval(*_args, **_kwargs):
        raise AssertionError("personal query must not be sent to a third-party embedding provider")
    monkeypatch.setattr("app.api.assistant.retrieve_context", forbidden_retrieval)
    faculty = Faculty(name="Khoa AI riêng tư")
    database.add(faculty)
    database.flush()
    major = Major(code="900002", name="Ngành riêng tư", faculty_id=faculty.id, description="", duration_years=4,
                  tuition_per_year_vnd=1, admission_quota=1)
    first = User(email="ai-first@example.com", full_name="Sinh viên A", password_hash=hash_password("password"), role="student")
    second = User(email="ai-second@example.com", full_name="Sinh viên B", password_hash=hash_password("password"), role="student")
    database.add_all([major, first, second])
    database.flush()
    database.add_all([
        Student(user_id=first.id, student_number="STU-OWN", full_name=first.full_name, email=first.email, major_id=major.id),
        Student(user_id=second.id, student_number="STU-OTHER", full_name=second.full_name, email=second.email, major_id=major.id),
    ])
    database.commit()
    headers = {"Authorization": f"Bearer {create_token(first.id)}"}
    conversation = client.post("/api/v1/assistant/conversations", headers=headers, json={}).json()
    response = client.post(f"/api/v1/assistant/conversations/{conversation['id']}/messages", headers=headers,
                           json={"message": "Mã sinh viên của tôi là gì?"})
    assert response.status_code == 200
    answer = response.json()["message"]["content"]
    assert "STU-OWN" in answer
    assert "STU-OTHER" not in answer


def test_chat_does_not_forward_private_history_to_cloud(client, database, monkeypatch):
    from app.ai.providers import ProviderStreamEvent, provider_manager
    from app.core.config import settings
    monkeypatch.setattr(settings, "ai_provider", "gemini")
    monkeypatch.setattr(settings, "gemini_api_key", "test-key")
    monkeypatch.setattr(settings, "groq_api_key", None)
    user = User(email="private-history@example.com", full_name="Sinh viên", password_hash=hash_password("password"), role="student")
    database.add(user)
    database.commit()
    headers = {"Authorization": f"Bearer {create_token(user.id)}"}
    conversation = client.post("/api/v1/assistant/conversations", headers=headers, json={}).json()
    first = client.post(f"/api/v1/assistant/conversations/{conversation['id']}/messages", headers=headers,
                        json={"message": "Mã sinh viên của tôi là gì?"})
    assert first.status_code == 200
    forwarded_history = []

    async def fake_stream(_system, history, _question, *, allow_fallback=True, on_status=None, budget_seconds=None):
        forwarded_history.extend(history)
        yield ProviderStreamEvent("token", text="GPA là điểm trung bình học tập.", provider="gemini", model="fake-model")
        yield ProviderStreamEvent("complete", provider="gemini", model="fake-model")

    monkeypatch.setattr(provider_manager, "stream", fake_stream)
    second = client.post(f"/api/v1/assistant/conversations/{conversation['id']}/messages", headers=headers,
                         json={"message": "GPA là gì?"})
    assert second.status_code == 200
    assert forwarded_history == []
