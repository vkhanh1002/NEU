from sqlalchemy import func, select

from app.core.security import create_token
from app.models import CourseEnrollment, CourseOffering, Personnel, Student, User


def auth(user):
    return {"Authorization": f"Bearer {create_token(user.id)}"}


def test_camera_evidence_makeup_review_updates_attendance_and_keeps_scope(client, database, monkeypatch, tmp_path):
    from app import seed
    from app.api import attendance
    from sqlalchemy.orm import sessionmaker

    monkeypatch.setattr(seed, "engine", database.get_bind())
    monkeypatch.setattr(seed, "SessionLocal", sessionmaker(bind=database.get_bind(), autoflush=False, expire_on_commit=False))
    monkeypatch.setattr(seed, "enable_vector_extension", lambda: None)
    monkeypatch.setattr(attendance, "UPLOAD_DIR", tmp_path)
    seed.seed_data()
    seed.seed_data()

    lecturer_user = database.scalar(select(User).where(User.email == "lecturer@neu.local"))
    lecturer = database.scalar(select(Personnel).where(Personnel.user_id == lecturer_user.id))
    offering = database.scalar(select(CourseOffering).where(CourseOffering.lecturer_id == lecturer.id))
    classes = client.get("/api/v1/lecturer/classes", headers=auth(lecturer_user))
    assert classes.status_code == 200
    demo_classes = [row for row in classes.json()["items"] if row["section"] == "D02"]
    assert len(demo_classes) >= 6
    demo_rosters = {
        tuple(row["student_number"] for row in client.get(
            f"/api/v1/lecturer/classes/{item['id']}/students", headers=auth(lecturer_user)
        ).json()["items"])
        for item in demo_classes
    }
    assert len(demo_rosters) >= 6
    roster = client.get(f"/api/v1/lecturer/classes/{offering.id}/students", headers=auth(lecturer_user))
    assert roster.status_code == 200 and roster.json()["count"] > 0
    assert roster.json()["offering"]["id"] == offering.id
    enrolled_count = database.scalar(select(func.count(CourseEnrollment.id)).where(CourseEnrollment.offering_id == offering.id))
    students = database.scalars(select(Student).join(CourseEnrollment)
                                .where(CourseEnrollment.offering_id == offering.id)
                                .order_by(Student.student_number).limit(2)).all()
    assert len(students) == 2
    student_users = [database.get(User, student.user_id) for student in students]

    bad_grade = client.patch(f"/api/v1/lecturer/classes/{offering.id}/grades/{students[0].id}",
                             headers=auth(lecturer_user), json={"midterm_score": 11})
    assert bad_grade.status_code == 422
    updated_grade = client.patch(f"/api/v1/lecturer/classes/{offering.id}/grades/{students[0].id}",
                                 headers=auth(lecturer_user), json={"attendance_score": 9.5, "midterm_score": 8.0})
    assert updated_grade.status_code == 200 and updated_grade.json()["attendance_score"] == 9.5
    grade_history = client.get(f"/api/v1/lecturer/classes/{offering.id}/grades/audit", headers=auth(lecturer_user))
    assert grade_history.status_code == 200 and grade_history.json()["items"][0]["new_values"]["midterm_score"] == 8.0

    opened = client.post("/api/v1/lecturer/attendance/sessions", headers=auth(lecturer_user), json={"offering_id": offering.id})
    assert opened.status_code == 201, opened.text
    session_id = opened.json()["id"]
    photo = b"\xff\xd8\xff" + b"camera-test-image"
    evidence_ids = []
    for student_user in student_users:
        evidence = client.post(f"/api/v1/student/attendance/sessions/{session_id}/evidence", headers=auth(student_user),
                               files={"photo": ("capture.jpg", photo, "image/jpeg")})
        assert evidence.status_code == 201, evidence.text
        evidence_ids.append(evidence.json()["id"])
    closed = client.post(f"/api/v1/lecturer/attendance/sessions/{session_id}/close", headers=auth(lecturer_user))
    assert closed.status_code == 200 and closed.json()["absent"] == enrolled_count

    requests = []
    for student_user, student in zip(student_users, students):
        record = client.get("/api/v1/student/attendance", headers=auth(student_user)).json()["items"][0]
        assert record["status"] == "absent" and record["can_submit_request"]
        submitted = client.post(f"/api/v1/student/attendance/records/{record['record_id']}/makeup-requests",
                                headers=auth(student_user), json={"reason": "Tôi có mặt trong lớp nhưng giảng viên chưa ghi nhận."})
        assert submitted.status_code == 201, submitted.text
        requests.append(submitted.json()["id"])
        duplicate = client.post(f"/api/v1/student/attendance/records/{record['record_id']}/makeup-requests",
                                headers=auth(student_user), json={"reason": "Tôi xin cập nhật điểm danh buổi này."})
        assert duplicate.status_code == 409

    lecturer_requests = client.get("/api/v1/lecturer/attendance/requests", headers=auth(lecturer_user))
    assert lecturer_requests.status_code == 200 and len(lecturer_requests.json()["items"]) == 2
    assert lecturer_requests.json()["pending_count"] == 2
    assert lecturer_requests.json()["items"][0]["request_reason"].startswith("Tôi có mặt")
    course_filter = client.get(f"/api/v1/lecturer/attendance/requests?course_id={offering.course_id}", headers=auth(lecturer_user))
    assert course_filter.status_code == 200
    assert all(row["course_code"] == offering.course.code for row in course_filter.json()["items"])
    assert client.get(f"/api/v1/attendance/evidence/{evidence_ids[0]}", headers=auth(lecturer_user)).status_code == 200
    assert client.patch(f"/api/v1/lecturer/attendance/requests/{requests[0]}", headers=auth(lecturer_user),
                        json={"decision": "rejected"}).status_code == 422
    assert client.patch(f"/api/v1/lecturer/attendance/requests/{requests[0]}", headers=auth(lecturer_user),
                        json={"decision": "accepted"}).json()["attendance_status"] == "late"
    assert client.patch(f"/api/v1/lecturer/attendance/requests/{requests[1]}", headers=auth(lecturer_user),
                        json={"decision": "rejected", "reason": "Ảnh chưa thể hiện rõ buổi học."}).json()["attendance_status"] == "absent"
    assert client.get("/api/v1/lecturer/attendance/requests?status=pending", headers=auth(lecturer_user)).json()["pending_count"] == 0

    accepted = client.get("/api/v1/student/attendance", headers=auth(student_users[0])).json()["items"][0]
    rejected = client.get("/api/v1/student/attendance", headers=auth(student_users[1])).json()["items"][0]
    assert accepted["status"] == "late" and accepted["makeup_request"]["status"] == "accepted"
    assert rejected["status"] == "absent" and rejected["makeup_request"]["reason"] == "Ảnh chưa thể hiện rõ buổi học."
    assert accepted["makeup_request"]["request_reason"].startswith("Tôi có mặt")
    assert client.get("/api/v1/notifications", headers=auth(student_users[0])).json()["unread_count"] >= 1

    not_enrolled = next(student for student in database.scalars(select(Student).order_by(Student.student_number)).all()
                        if not database.scalar(select(CourseEnrollment.id).where(
                            CourseEnrollment.offering_id == offering.id, CourseEnrollment.student_id == student.id)))
    lookup = client.get(f"/api/v1/lecturer/classes/{offering.id}/students/lookup?student_number={not_enrolled.student_number}",
                        headers=auth(lecturer_user))
    assert lookup.status_code == 200 and lookup.json()["student_id"] == not_enrolled.id
    added = client.post(f"/api/v1/lecturer/classes/{offering.id}/students", headers=auth(lecturer_user),
                        json={"student_number": not_enrolled.student_number})
    assert added.status_code == 201
    duplicate_enrollment = client.post(f"/api/v1/lecturer/classes/{offering.id}/students", headers=auth(lecturer_user),
                                       json={"student_number": not_enrolled.student_number})
    assert duplicate_enrollment.status_code == 409

