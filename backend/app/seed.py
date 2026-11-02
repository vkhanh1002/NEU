from datetime import date, datetime, time, timedelta, timezone

from sqlalchemy import select

from app.core.database import Base, SessionLocal, enable_vector_extension, engine
from app.core.security import hash_password, verify_password
from app.models import (Applicant, Assignment, AssignmentSubmission, ConductRecord, Course, CourseEnrollment,
                        CourseOffering, Exam, FAQ, Faculty, Major, NewsArticle, Notification, PaymentTransaction,
                        Personnel, Semester, Student, StudentCharge, SupportTicket, UniversityEvent, User)
from app.services.schedule import STUDY_SHIFTS


MAJOR_DATA = [
    ("7480201", "Công nghệ thông tin", "Đào tạo nền tảng phát triển phần mềm, dữ liệu và hệ thống máy tính.", "Khoa Công nghệ", 4, 28000000, 240),
    ("7480101", "Khoa học máy tính", "Tập trung vào thuật toán, trí tuệ nhân tạo và nền tảng tính toán.", "Khoa Công nghệ", 4, 29000000, 120),
    ("7480103", "Kỹ thuật phần mềm", "Phát triển kỹ năng phân tích, thiết kế, xây dựng và vận hành phần mềm.", "Khoa Công nghệ", 4, 28000000, 180),
    ("7480104", "Hệ thống thông tin", "Kết nối công nghệ thông tin với quy trình và dữ liệu tổ chức.", "Khoa Công nghệ", 4, 27000000, 120),
    ("7480202", "An toàn thông tin", "Kiến thức về bảo mật hệ thống, mạng và dữ liệu số.", "Khoa Công nghệ", 4, 30000000, 100),
    ("7340101", "Quản trị kinh doanh", "Kiến thức nền tảng về quản trị, vận hành và chiến lược kinh doanh.", "Khoa Kinh tế", 4, 25000000, 200),
    ("7340115", "Marketing", "Nghiên cứu thị trường, thương hiệu và truyền thông tiếp thị.", "Khoa Kinh tế", 4, 26000000, 160),
    ("7340301", "Kế toán", "Thông tin kế toán, báo cáo tài chính và kiểm soát nội bộ.", "Khoa Kinh tế", 4, 24000000, 150),
    ("7340201", "Tài chính – Ngân hàng", "Kiến thức về thị trường tài chính, ngân hàng và quản trị rủi ro.", "Khoa Kinh tế", 4, 26000000, 150),
    ("7220201", "Ngôn ngữ Anh", "Phát triển năng lực tiếng Anh và giao tiếp liên văn hóa.", "Khoa Ngoại ngữ", 4, 23000000, 180),
]

FAQ_DATA = [
    ("Hồ sơ đăng ký xét tuyển gồm những gì?", "Thành phần hồ sơ phụ thuộc phương thức và đợt tiếp nhận. Hãy kiểm tra hướng dẫn tuyển sinh đang áp dụng để chuẩn bị đúng giấy tờ và thời hạn.", "Tuyển sinh"),
    ("Làm thế nào để gửi yêu cầu hỗ trợ?", "Đăng nhập cổng sinh viên, mở Trung tâm hỗ trợ, chọn nhóm vấn đề, nhập tiêu đề và mô tả rồi gửi. Mã yêu cầu sẽ xuất hiện trong danh sách để bạn theo dõi.", "Hỗ trợ"),
    ("Tôi tra cứu tình trạng hồ sơ ở đâu?", "Mở mục Tuyển sinh và tra cứu bằng tài khoản đã đăng ký. Nhân viên có thể xem danh sách hồ sơ theo quyền được cấp.", "Tuyển sinh"),
    ("Học phí hiển thị trên hệ thống có chính thức không?", "Mức thu có thể thay đổi theo chương trình và năm học. Hãy đối chiếu thông báo tài chính được đơn vị phụ trách công bố trước khi thanh toán.", "Học phí"),
    ("Tài liệu nào được dùng làm nguồn cho trợ lý?", "Trợ lý tra cứu câu hỏi thường gặp, danh mục ngành và các tài liệu PDF, DOCX hoặc TXT được quản trị viên phê duyệt. Khi nguồn chưa đủ, trợ lý sẽ nêu rõ giới hạn.", "Hỗ trợ"),
]

STUDENT_GIVEN_NAMES = ["Minh Anh", "Gia Huy", "Phương Linh", "Hoàng Nam", "Thảo Vy", "Quốc Bảo", "Khánh Ngọc", "Tuấn Kiệt", "Hà My", "Đức Anh", "Bảo Trân", "Nhật Minh", "Thanh Tâm", "Quang Vinh", "Ngọc Hà", "Hữu Phước", "Mai Chi", "Trọng Nghĩa", "Yến Nhi", "Đình Khang", "Kim Anh", "Tiến Đạt", "Khánh Linh", "Đăng Khoa", "Thùy Dương", "Minh Quân", "Bích Ngọc", "Hoài An", "Văn Khải", "Hương Giang", "Anh Tuấn", "Ngọc Diệp", "Phúc Hưng", "Thanh Trúc", "Bảo Long", "Thu Trang", "Duy Khánh", "Quỳnh Mai", "Thành Đạt", "Như Ý"]
STUDENT_FAMILY_NAMES = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ", "Đặng", "Bùi", "Đỗ", "Hồ", "Ngô", "Dương"]
SAMPLE_ADDRESSES = ["Ba Đình, Hà Nội", "Cầu Giấy, Hà Nội", "Hải Châu, Đà Nẵng", "Ninh Kiều, Cần Thơ", "Quận 3, TP. Hồ Chí Minh", "Thủ Đức, TP. Hồ Chí Minh", "Biên Hòa, Đồng Nai", "Thành phố Huế"]

COURSE_DATA = [
    ("ECO101", "Kinh tế vi mô", 3), ("ACC101", "Nguyên lý kế toán", 3),
    ("MGT101", "Quản trị học", 3), ("MAT101", "Toán cao cấp", 3),
    ("LAW101", "Pháp luật đại cương", 2), ("ENG101", "Tiếng Anh học thuật", 3),
    ("STA101", "Thống kê ứng dụng", 3), ("FIN101", "Tài chính căn bản", 3),
    ("MKT101", "Marketing căn bản", 3), ("MIS101", "Hệ thống thông tin quản lý", 3),
]

NEWS_DATA = [
    ("lap-ke-hoach-hoc-tap", "Cách lập kế hoạch học tập cho một học kỳ", "Học tập", "Một kế hoạch ngắn gọn giúp chia mục tiêu lớn thành các đầu việc có thể theo dõi.", "Bắt đầu bằng việc ghi lại các môn học, thời hạn và mục tiêu cá nhân. Chia nhiệm vụ theo tuần, dành thời gian ôn tập định kỳ và cập nhật kế hoạch khi lịch học thay đổi. Đây là gợi ý học tập chung; lịch và quy định cụ thể cần được tra cứu từ đơn vị phụ trách.", "photo-1523050854058-8df90110c9f1"),
    ("doc-tai-lieu-hieu-qua", "Kỹ thuật đọc tài liệu và ghi chú chủ động", "Học tập", "Đọc có câu hỏi dẫn đường giúp người học tập trung vào ý chính và ghi nhớ tốt hơn.", "Trước khi đọc, hãy xác định điều cần tìm hiểu. Trong khi đọc, ghi lại luận điểm, dữ liệu cần kiểm tra và câu hỏi còn mở. Sau đó tóm tắt bằng lời của mình và đối chiếu với tài liệu gốc.", "photo-1456324504439-367cee3b3c32"),
    ("ky-nang-thuyet-trinh", "Chuẩn bị một bài thuyết trình học thuật", "Kỹ năng", "Một cấu trúc rõ ràng giúp người nghe theo dõi luận điểm và phần minh chứng.", "Hãy xác định thông điệp chính, sắp xếp nội dung theo trình tự dễ hiểu, ghi nguồn cho số liệu và luyện tập trong thời lượng dự kiến. Kết thúc bằng phần tổng kết và dành thời gian tiếp nhận câu hỏi.", "photo-1516321318423-f06f85e504b3"),
    ("tim-kiem-thong-tin", "Nhận biết và kiểm tra nguồn thông tin", "Kỹ năng", "Kiểm tra tác giả, ngày cập nhật và nguồn dẫn trước khi sử dụng thông tin.", "Khi tra cứu, ưu tiên tài liệu có cơ quan phát hành rõ ràng, kiểm tra thời điểm cập nhật và so sánh với nguồn độc lập. Với quy chế, lịch tuyển sinh hoặc học phí, hãy dùng thông báo được đơn vị có thẩm quyền công bố.", "photo-1453738773917-9c3eff1db985"),
    ("chuan-bi-ho-so", "Chuẩn bị hồ sơ theo hướng dẫn của từng đợt", "Tuyển sinh", "Danh mục hồ sơ có thể thay đổi theo phương thức và thời điểm tiếp nhận.", "Người đăng ký nên đọc hướng dẫn của đợt tuyển sinh đang áp dụng, kiểm tra yêu cầu về định dạng và thời hạn trước khi gửi. Bài viết này không thay thế thông báo tuyển sinh hoặc tư vấn từ đơn vị phụ trách.", "photo-1434030216411-0b793f4b4173"),
    ("hoi-dap-tu-van", "Cách chuẩn bị câu hỏi khi cần tư vấn ngành học", "Tuyển sinh", "Nêu rõ mối quan tâm giúp buổi tư vấn tập trung vào thông tin người học cần.", "Bạn có thể ghi lại lĩnh vực quan tâm, trải nghiệm học tập và câu hỏi về chương trình, môi trường học hoặc cơ hội nghề nghiệp. Những thông tin về chỉ tiêu, tổ hợp và điểm chuẩn cần được xác nhận theo tài liệu chính thức của từng năm.", "photo-1521737711867-e3b97375f902"),
    ("ket-noi-cong-dong", "Xây dựng thói quen kết nối trong môi trường đại học", "Cộng đồng", "Chủ động tham gia hoạt động học thuật giúp người học mở rộng góc nhìn và kết nối.", "Bắt đầu từ một câu lạc bộ, buổi tọa đàm hoặc nhóm học tập phù hợp với lịch cá nhân. Hãy tìm thông tin hoạt động qua kênh của đơn vị tổ chức và cân nhắc mục tiêu, thời gian tham gia.", "photo-1523240795612-9a054b0db644"),
    ("bao-ve-suc-khoe-hoc-duong", "Cân bằng thời gian học tập và nghỉ ngơi", "Đời sống sinh viên", "Một lịch sinh hoạt ổn định hỗ trợ duy trì sự tập trung trong thời gian học tập.", "Xen kẽ các phiên học với nghỉ ngắn, giữ lịch ngủ phù hợp và tìm hỗ trợ khi áp lực kéo dài. Mỗi người có nhịp sinh hoạt khác nhau; nên chọn cách điều chỉnh phù hợp với hoàn cảnh của mình.", "photo-1506126613408-eca07ce68773"),
    ("su-dung-tro-ly-so", "Đặt câu hỏi hiệu quả với trợ lý học tập", "Công nghệ", "Nêu bối cảnh và kết quả mong muốn để nhận câu trả lời sát nhu cầu hơn.", "Hãy mô tả chủ đề, mức độ kiến thức và định dạng mong muốn. Với câu hỏi về quy định hoặc thông tin cá nhân, hãy kiểm tra nguồn tham khảo và đối chiếu với hệ thống hay đơn vị có thẩm quyền.", "photo-1516321318423-f06f85e504b3"),
    ("ky-nang-lam-viec-nhom", "Phân công công việc trong dự án nhóm", "Kỹ năng", "Mục tiêu, đầu việc và thời hạn rõ ràng giúp nhóm phối hợp minh bạch.", "Thống nhất kết quả cần bàn giao, chia đầu việc theo năng lực và cập nhật tiến độ ở một nơi chung. Khi có bất đồng, quay lại tiêu chí đánh giá và trao đổi trực tiếp để thống nhất cách xử lý.", "photo-1528605248644-14dd04022da1"),
    ("huong-dan-su-dung-cong-sinh-vien", "Quản lý thông tin học tập trên cổng sinh viên", "Hướng dẫn", "Kiểm tra hồ sơ, thời khóa biểu, kết quả và thông báo trong từng khu vực chức năng.", "Sau khi đăng nhập, mở từng mục trên thanh điều hướng để xem dữ liệu gắn với tài khoản. Nếu thông tin chưa chính xác hoặc chức năng không truy cập được, hãy gửi yêu cầu hỗ trợ và cung cấp mã hồ sơ thay vì chia sẻ mật khẩu.", "photo-1519389950473-47ba0277781c"),
]


def seed_academic_news(db) -> None:
    """Add stable, linked sample records without replacing existing user data."""
    now = datetime.now(timezone.utc)
    semesters = {}
    for code, name, year, start, end, current in [
        ("2025-2", "Học kỳ 2 năm học 2025–2026", "2025–2026", date(2026, 2, 1), date(2026, 6, 30), False),
        ("2026-1", "Học kỳ 1 năm học 2026–2027", "2026–2027", date(2026, 9, 1), date(2027, 1, 31), True),
    ]:
        row = db.scalar(select(Semester).where(Semester.code == code))
        if not row:
            row = Semester(code=code, name=name, academic_year=year, starts_on=start, ends_on=end, is_current=current)
            db.add(row)
        else:
            row.is_current = current
        semesters[code] = row
    db.flush()

    linked = db.scalars(select(Student).where(Student.user_id.is_not(None)).order_by(Student.student_number)).all()
    remaining = db.scalars(select(Student).where(Student.user_id.is_(None)).order_by(Student.student_number).limit(20)).all()
    students = (linked + remaining)[:20]
    majors = db.scalars(select(Major).order_by(Major.code)).all()
    lecturers = db.scalars(select(Personnel).where(Personnel.kind == "lecturer").order_by(Personnel.code)).all()
    student_users: list[User] = []
    for index, student in enumerate(students, start=1):
        account = db.get(User, student.user_id) if student.user_id else None
        if account is None:
            email = "student@neu.local" if index == 1 else f"student{index:02d}@neu.local"
            account = db.scalar(select(User).where(User.email == email))
            if not account:
                account = User(email=email, full_name=student.full_name,
                               password_hash=hash_password("NEUStudent2026!"), role="student")
                db.add(account)
                db.flush()
            student.user_id = account.id
        student_users.append(account)
    db.flush()

    courses = {}
    for index, (code, name, credits) in enumerate(COURSE_DATA):
        course = db.scalar(select(Course).where(Course.code == code))
        if not course:
            course = Course(code=code, name=name, credits=credits,
                            major_id=majors[index % len(majors)].id if majors else None)
            db.add(course)
            db.flush()
        courses[code] = course

    offerings = {}
    for semester_index, term_code in enumerate(("2025-2", "2026-1")):
        semester = semesters[term_code]
        for course_index, (course_code, _, _) in enumerate(COURSE_DATA):
            offering = db.scalar(select(CourseOffering).where(
                CourseOffering.course_id == courses[course_code].id,
                CourseOffering.semester_id == semester.id,
                CourseOffering.section == "01",
            ))
            if not offering:
                weekday_index = course_index % 5 if semester_index == 1 else (course_index + 2) % 5
                shift_name, shift_start, shift_end = STUDY_SHIFTS[(course_index + semester_index) % len(STUDY_SHIFTS)]
                offering = CourseOffering(
                    course_id=courses[course_code].id, semester_id=semester.id,
                    lecturer_id=lecturers[course_index % len(lecturers)].id if lecturers else None,
                    section="01", room=f"A{101 + course_index}", delivery_mode="Trực tiếp",
                    weekday=weekday_index + 1, starts_at=time.fromisoformat(shift_start), ends_at=time.fromisoformat(shift_end),
                    note=f"Lịch mẫu {shift_name}; khung giờ cần được đơn vị đào tạo xác nhận.",
                )
                db.add(offering)
                db.flush()
            offerings[(term_code, course_code)] = offering

    for student_index, student in enumerate(students):
        for term_code, course_start in (("2025-2", 0), ("2026-1", 5)):
            for local_index in range(5):
                course_index = course_start + local_index
                course_code = COURSE_DATA[course_index][0]
                offering = offerings[(term_code, course_code)]
                enrollment = db.scalar(select(CourseEnrollment).where(
                    CourseEnrollment.student_id == student.id,
                    CourseEnrollment.offering_id == offering.id,
                ))
                if not enrollment:
                    if term_code == "2025-2":
                        score = (94, 86, 78, 64, 47)[(student_index + local_index) % 5]
                        letter = "A" if score >= 90 else "B" if score >= 80 else "C" if score >= 70 else "D" if score >= 50 else "F"
                        enrollment = CourseEnrollment(
                            student_id=student.id, offering_id=offering.id,
                            attendance_score=min(10, round(score / 10, 1)), midterm_score=min(10, round(score / 10, 1)),
                            final_score=min(10, round(score / 10, 1)), total_score=score / 10,
                            letter_grade=letter, status="Hoàn thành",
                        )
                    else:
                        enrollment = CourseEnrollment(student_id=student.id, offering_id=offering.id, status="Đang học")
                    db.add(enrollment)
                    db.flush()

                if term_code == "2026-1":
                    exam_exists = db.scalar(select(Exam.id).where(Exam.offering_id == offering.id))
                    if not exam_exists:
                        exam_day = now.date() + timedelta(days=28 + local_index * 2)
                        db.add(Exam(offering_id=offering.id,
                                    starts_at=datetime.combine(exam_day, time(8 + local_index % 2 * 3, 0), timezone.utc),
                                    room=f"B{201 + local_index}", exam_type="Trực tiếp", duration_minutes=90,
                                    note="Vui lòng kiểm tra lịch cá nhân trước ngày thi."))
                    assignment = db.scalar(select(Assignment).where(
                        Assignment.offering_id == offering.id,
                        Assignment.title == f"Bài tập học kỳ · {course_code}",
                    ))
                    if not assignment:
                        due = now + timedelta(days=(-1 if local_index == 0 else 3 + local_index * 2))
                        assignment = Assignment(
                            offering_id=offering.id, title=f"Bài tập học kỳ · {course_code}",
                            description=f"Tổng hợp và trình bày nội dung trọng tâm của học phần {COURSE_DATA[course_index][1]}.",
                            assigned_at=now - timedelta(days=7), deadline=due,
                        )
                        db.add(assignment)
                        db.flush()
                    submission = db.scalar(select(AssignmentSubmission).where(
                        AssignmentSubmission.assignment_id == assignment.id,
                        AssignmentSubmission.student_id == student.id,
                    ))
                    if not submission:
                        state = ("Đã chấm", "Đã nộp", "Đang thực hiện", "Chưa làm", "Quá hạn")[(student_index + local_index) % 5]
                        if state == "Quá hạn" and local_index != 0:
                            state = "Chưa làm"
                        submitted = state in {"Đã chấm", "Đã nộp"}
                        db.add(AssignmentSubmission(
                            assignment_id=assignment.id, student_id=student.id,
                            submitted_at=now - timedelta(days=1) if submitted else None,
                            status=state, content="Đã hoàn thành nội dung bài tập." if submitted else "",
                            score=8.0 if state == "Đã chấm" else None,
                        ))

            if term_code == "2025-2":
                conduct_score = 65 + (student_index * 7) % 36
                existing = db.scalar(select(ConductRecord.id).where(
                    ConductRecord.student_id == student.id, ConductRecord.semester_id == semesters[term_code].id))
                if not existing:
                    db.add(ConductRecord(student_id=student.id, semester_id=semesters[term_code].id,
                                         score=conduct_score, rating="Xuất sắc" if conduct_score >= 90 else "Tốt" if conduct_score >= 80 else "Khá" if conduct_score >= 65 else "Trung bình",
                                         comment="Đánh giá theo kết quả rèn luyện trong học kỳ.", status="Đã công bố",
                                         evaluated_at=datetime(2026, 7, 5, tzinfo=timezone.utc)))

        current_term = semesters["2026-1"]
        current_conduct = db.scalar(select(ConductRecord.id).where(
            ConductRecord.student_id == student.id, ConductRecord.semester_id == current_term.id))
        if not current_conduct:
            db.add(ConductRecord(student_id=student.id, semester_id=current_term.id,
                                 score=0, rating="Đang đánh giá", comment="Kết quả sẽ được cập nhật khi kết thúc học kỳ.",
                                 status="Đang đánh giá"))

        for term_code, amount in (("2025-2", 12_000_000), ("2026-1", 14_000_000)):
            term = semesters[term_code]
            charge_title = f"Học phí học kỳ {term_code}"
            charge = db.scalar(select(StudentCharge).where(
                StudentCharge.student_id == student.id, StudentCharge.semester_id == term.id,
                StudentCharge.title == charge_title,
            ))
            if not charge:
                charge = StudentCharge(student_id=student.id, semester_id=term.id, title=charge_title,
                                       amount_due=amount, due_date=term.ends_on - timedelta(days=10))
                db.add(charge)
                db.flush()
                if (student_index + (0 if term_code == "2025-2" else 1)) % 3 != 0:
                    paid = amount if student_index % 2 else amount // 2
                    db.add(PaymentTransaction(charge_id=charge.id, amount=paid,
                                              paid_at=datetime.combine(term.starts_on + timedelta(days=15), time(10, 0), timezone.utc),
                                              reference=f"TX-{student.student_number}-{term_code}",
                                              note="Giao dịch được ghi nhận trong sổ thu."))

        if student.user_id:
            for title, message, href in [
                ("Lịch học học kỳ hiện tại", "Thời khóa biểu học kỳ đã được cập nhật.", "/student/schedule"),
                ("Kiểm tra bài tập sắp đến hạn", "Mở mục Bài tập để xem hạn nộp từng học phần.", "/student/assignments"),
                ("Tra cứu khoản thu", "Thông tin khoản thu và giao dịch được cập nhật trong mục Tài chính.", "/student/finance"),
            ]:
                exists = db.scalar(select(Notification.id).where(
                    Notification.owner_id == student.user_id, Notification.title == title,
                    Notification.href == href,
                ))
                if not exists:
                    db.add(Notification(owner_id=student.user_id, title=title, message=message, href=href))
            ticket_code = f"ST-{student.student_number[-12:]}"
            if not db.scalar(select(SupportTicket.id).where(SupportTicket.code == ticket_code)):
                db.add(SupportTicket(code=ticket_code, owner_id=student.user_id, category="Đào tạo và học tập",
                                     subject="Tra cứu lịch học và kết quả học tập",
                                     description="Yêu cầu hỗ trợ về thông tin học tập trong tài khoản.",
                                     priority="Bình thường",
                                     status=("Mới tiếp nhận", "Đang xử lý", "Đã giải quyết")[student_index % 3]))

    statuses = ("Mới tiếp nhận", "Cần bổ sung", "Đang xét duyệt", "Đã duyệt", "Trúng tuyển", "Không đủ điều kiện", "Không trúng tuyển")
    review_notes = {
        "Cần bổ sung": "Vui lòng kiểm tra danh mục giấy tờ và cập nhật phần còn thiếu trong tài khoản.",
        "Đang xét duyệt": "Hồ sơ đang được rà soát; trạng thái sẽ cập nhật sau khi có kết quả.",
        "Đã duyệt": "Thông tin hồ sơ đã được kiểm tra ở bước tiếp nhận.",
        "Trúng tuyển": "Hồ sơ đã được ghi nhận ở trạng thái trúng tuyển trong dữ liệu của hệ thống.",
        "Không đủ điều kiện": "Hồ sơ chưa đáp ứng điều kiện trong dữ liệu xét duyệt hiện tại.",
        "Không trúng tuyển": "Hồ sơ đã kết thúc quy trình xét tuyển trong dữ liệu của hệ thống.",
    }
    for index in range(24):
        email = f"candidate{index + 1:02d}@example.test"
        if db.scalar(select(Applicant.id).where(Applicant.email == email)):
            continue
        major = majors[index % len(majors)]
        db.add(Applicant(
            email=email, full_name=f"Thí sinh {index + 1:02d}", phone=f"0908{index:06d}",
            date_of_birth=date(2006, index % 12 + 1, index % 27 + 1),
            address=SAMPLE_ADDRESSES[index % len(SAMPLE_ADDRESSES)], desired_major_id=major.id,
            admission_method=("Học bạ", "Điểm thi tốt nghiệp", "Đánh giá năng lực")[index % 3],
            status=statuses[index % len(statuses)],
            review_note=review_notes.get(statuses[index % len(statuses)], ""),
        ))
    db.flush()
    for index in range(1, 6):
        email = f"candidate{index:02d}@example.test"
        applicant = db.scalar(select(Applicant).where(Applicant.email == email))
        account = db.scalar(select(User).where(User.email == email))
        if applicant and not account:
            db.add(User(email=email, full_name=applicant.full_name,
                        password_hash=hash_password("NEUApplicant2026!"), role="applicant"))

    for index, (slug, title, category, summary, content, photo) in enumerate(NEWS_DATA):
        if not db.scalar(select(NewsArticle.id).where(NewsArticle.slug == slug)):
            db.add(NewsArticle(
                slug=slug, title=title, category=category, summary=summary, content=content,
                image_url=f"https://images.unsplash.com/{photo}?auto=format&fit=crop&w=1200&q=80",
                published_at=now - timedelta(days=index + 1), status="published",
            ))

    # These draft event records are kept for staff review and are not exposed as confirmed public events.
    events = [
        ("Trao đổi phương pháp tự học bậc đại học", "Học thuật", "Chia sẻ cách lập kế hoạch và tự đánh giá tiến độ học tập."),
        ("Chuyên đề kỹ năng nghiên cứu", "Học thuật", "Thảo luận về cách tìm, đánh giá và trích dẫn nguồn học thuật."),
        ("Tọa đàm định hướng nghề nghiệp", "Nghề nghiệp", "Trao đổi về cách tìm hiểu lĩnh vực nghề nghiệp và chuẩn bị kỹ năng."),
        ("Sinh hoạt câu lạc bộ học tập", "Sinh viên", "Không gian kết nối nhóm học tập và chia sẻ kinh nghiệm."),
        ("Hỏi đáp về thủ tục sinh viên", "Hỗ trợ người học", "Phiên hỏi đáp để tiếp nhận các câu hỏi về quy trình dịch vụ."),
    ]
    for index, (title, category, summary) in enumerate(events):
        if not db.scalar(select(UniversityEvent.id).where(UniversityEvent.title == title)):
            start = now + timedelta(days=14 + index * 7)
            db.add(UniversityEvent(title=title, category=category, summary=summary,
                                   location="Địa điểm sẽ được cập nhật sau khi phê duyệt lịch.",
                                   starts_at=start, ends_at=start + timedelta(hours=2), status="draft"))


def seed_data() -> None:
    enable_vector_extension()
    # Repair an interrupted/partially initialized database before checking seed state.
    # Alembic remains the schema migration mechanism; create_all is idempotent and
    # ensures the initial tables exist if a prior startup recorded the revision early.
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        faculties: dict[str, Faculty] = {}
        for faculty_name in sorted({row[3] for row in MAJOR_DATA}):
            faculty = db.scalar(select(Faculty).where(Faculty.name == faculty_name))
            if not faculty:
                faculty = Faculty(name=faculty_name)
                db.add(faculty)
                db.flush()
            faculties[faculty_name] = faculty
        db.flush()
        majors: dict[str, Major] = {}
        for code, name, description, faculty, years, tuition, quota in MAJOR_DATA:
            major = db.scalar(select(Major).where(Major.code == code))
            if not major:
                major = Major(code=code, name=name, description=description, faculty_id=faculties[faculty].id,
                              duration_years=years, tuition_per_year_vnd=tuition, admission_quota=quota,
                              admission_status="Đang tuyển sinh", is_demo=True)
                db.add(major)
                db.flush()
            majors[name] = major

        demo_accounts = [
            ("admin@neu.local", "Quản trị NEU", "super_admin", "admin@study.edu.vn"),
            ("admissions@neu.local", "Nguyễn Minh Anh", "admission_staff", "admissions@study.edu.vn"),
            ("student@neu.local", "Trần Minh Khoa", "student", "student@study.edu.vn"),
            ("support@neu.local", "Lê Thu Hà", "support_staff", "support@study.edu.vn"),
            ("hr@neu.local", "Cán bộ nhân sự", "hr_staff", None),
            ("academic@neu.local", "Cán bộ đào tạo", "academic_staff", None),
            ("lecturer@neu.local", "Giảng viên NEU", "lecturer", None),
        ]
        users: dict[str, User] = {}
        for email, name, role, legacy_email in demo_accounts:
            account = db.scalar(select(User).where(User.email == email))
            migrated = False
            if not account and legacy_email:
                account = db.scalar(select(User).where(User.email == legacy_email))
                if account:
                    migrated = True
                    account.email = email
                    if verify_password("StudyDemo2026!", account.password_hash):
                        migrated_password = "NEUStudent2026!" if role == "student" else "NEUStaff2026!"
                        account.password_hash = hash_password(migrated_password)
                    profile = db.scalar(select(Student).where(Student.user_id == account.id))
                    if profile and profile.email == legacy_email:
                        profile.email = email
            if not account:
                password = "NEUStudent2026!" if role == "student" else "NEUStaff2026!"
                account = User(email=email, full_name=name, password_hash=hash_password(password), role=role)
                db.add(account)
                db.flush()
            elif role == "super_admin" and migrated and account.full_name == "Quản trị Study":
                account.full_name = name
            users[email] = account
        admin = users["admin@neu.local"]
        admissions = users["admissions@neu.local"]
        student_user = users["student@neu.local"]
        support_user = users["support@neu.local"]
        db.flush()

        if (not db.scalar(select(Student.id).where(Student.student_number == "STU20260001"))
                and not db.scalar(select(Student.id).where(Student.user_id == student_user.id))):
            db.add(Student(user_id=student_user.id, student_number="STU20260001", full_name=student_user.full_name,
                           email=student_user.email, phone="0900000001", major_id=majors["Công nghệ thông tin"].id,
                           cohort="2026", class_name="CNTT-K26A", study_status="Đang học",
                           enrollment_date=date(2026, 9, 5), is_demo=True))

        # Stable unique codes make this additive seed safe to rerun. Existing rows are never updated.
        for index, given_name in enumerate(STUDENT_GIVEN_NAMES[:19], start=2):
            cohort_year = (2022, 2023, 2024, 2025, 2026)[index % 5]
            cohort = str(cohort_year)
            student_number = f"STU{cohort}{index:04d}"
            sample_email = f"sv{index:02d}@example.com"
            if (db.scalar(select(Student.id).where(Student.student_number == student_number))
                    or db.scalar(select(Student.id).where(Student.email == sample_email))):
                continue
            major = list(majors.values())[(index - 2) % len(majors)]
            family = STUDENT_FAMILY_NAMES[(index * 3) % len(STUDENT_FAMILY_NAMES)]
            full_name = f"{family} {given_name}"
            study_status = "Tạm nghỉ" if index % 13 == 0 else ("Đã tốt nghiệp" if cohort_year < 2023 else ("Bảo lưu" if index % 11 == 0 else "Đang học"))
            db.add(Student(student_number=student_number, full_name=full_name,
                           email=sample_email, phone=f"09{index % 10}{index:07d}",
                           date_of_birth=date(2002 + index % 5, index % 12 + 1, index % 27 + 1),
                           gender=("Nam", "Nữ", "Khác")[index % 3], address=SAMPLE_ADDRESSES[index % len(SAMPLE_ADDRESSES)],
                           major_id=major.id, cohort=cohort, class_name=f"{major.code[-3:]}-K{cohort[-2:]}{chr(65 + index % 3)}",
                           study_status=study_status, enrollment_date=date(cohort_year, 9, 5), is_demo=True))

        lecturer_names = ["Nguyễn Thị Hồng Nhung", "Trần Quốc Bảo", "Lê Minh Phương", "Phạm Văn Thành", "Vũ Thu Hà", "Đặng Hoàng Long", "Bùi Ngọc Anh"]
        faculties_by_name = {faculty.name: faculty for faculty in faculties.values()}
        for index, full_name in enumerate(lecturer_names, start=1):
            code = f"GV-NEU-{index:03d}"
            email = f"giangvien{index:02d}@example.com"
            existing_personnel = db.scalar(select(Personnel).where(Personnel.email == email))
            if existing_personnel:
                if existing_personnel.code.startswith("GV-DEMO-"):
                    existing_personnel.code = code
                existing_personnel.notes = ""
                continue
            if db.scalar(select(Personnel.id).where(Personnel.code == code)):
                continue
            faculty_name = ("Khoa Công nghệ", "Khoa Kinh tế", "Khoa Ngoại ngữ")[index % 3]
            faculty = faculties_by_name[faculty_name]
            db.add(Personnel(code=code, kind="lecturer", full_name=full_name,
                             email=email, phone=f"090700{index:04d}",
                             date_of_birth=date(1975 + index % 15, index % 12 + 1, index % 27 + 1),
                             gender="Nữ" if index % 2 else "Nam", address=SAMPLE_ADDRESSES[index % len(SAMPLE_ADDRESSES)],
                             education_level=("Tiến sĩ", "Thạc sĩ")[index % 2],
                             academic_rank=("Phó Giáo sư" if index % 4 == 0 else ""),
                             specialty=faculty_name.replace("Khoa ", ""), faculty_id=faculty.id,
                             department=faculty_name, position="Giảng viên", start_date=date(2012 + index % 10, 9, 1),
                             work_status="Tạm nghỉ" if index == 12 else "Đang công tác", notes="", is_demo=True))

        employee_records = [
            ("NV-NEU-001", "Phạm Thu Hằng", "Phòng Công tác sinh viên", "Chuyên viên hỗ trợ"),
            ("NV-NEU-002", "Nguyễn Thành Trung", "Phòng Đào tạo", "Chuyên viên đào tạo"),
            ("NV-NEU-003", "Lê Khánh Vy", "Phòng Tài chính", "Kế toán viên"),
            ("NV-NEU-004", "Trần Minh Đức", "Phòng Công nghệ thông tin", "Quản trị hệ thống"),
            ("NV-NEU-005", "Võ Ngọc Diễm", "Phòng Tuyển sinh", "Chuyên viên tuyển sinh"),
            ("NV-NEU-006", "Bùi Quốc Khánh", "Thư viện", "Thủ thư"),
            ("NV-NEU-007", "Đặng Mỹ Linh", "Phòng Công tác sinh viên", "Chuyên viên hồ sơ"),
            ("NV-NEU-008", "Hồ Anh Tuấn", "Phòng Hành chính", "Chuyên viên hành chính"),
        ]
        for index, (code, full_name, department, position) in enumerate(employee_records, start=1):
            email = f"nhanvien{index:02d}@example.com"
            existing_personnel = db.scalar(select(Personnel).where(Personnel.email == email))
            if existing_personnel:
                if existing_personnel.code.startswith("NV-DEMO-"):
                    existing_personnel.code = code
                existing_personnel.notes = ""
                continue
            if db.scalar(select(Personnel.id).where(Personnel.code == code)):
                continue
            db.add(Personnel(code=code, kind="employee", full_name=full_name,
                             email=email, phone=f"090600{index:04d}",
                             date_of_birth=date(1985 + index % 10, index % 12 + 1, index % 27 + 1),
                             gender="Nữ" if index % 2 else "Nam", address=SAMPLE_ADDRESSES[(index + 2) % len(SAMPLE_ADDRESSES)],
                             department=department, position=position, start_date=date(2018 + index % 7, 3, 15),
                             work_status="Đã nghỉ việc" if index == 8 else "Đang công tác",
                             notes="", is_demo=True))

        existing_applicant = db.scalar(select(Applicant).where(Applicant.email == "ngoc.mai@example.edu.vn"))
        if existing_applicant:
            existing_applicant.admission_method = "Học bạ"
        else:
            db.add(Applicant(email="ngoc.mai@example.edu.vn", full_name="Phạm Ngọc Mai", phone="0900000012",
                             desired_major_id=majors["Marketing"].id, admission_method="Học bạ", status="Đang xét duyệt"))
        legacy_tickets = db.scalars(select(SupportTicket).where(SupportTicket.code.like("ST-DEMO10%"))).all()
        for ticket in legacy_tickets:
            updated_code = ticket.code.replace("ST-DEMO", "ST-NEU")
            if not db.scalar(select(SupportTicket.id).where(SupportTicket.code == updated_code)):
                ticket.code = updated_code
            if "mẫu" in ticket.description.lower() or "minh họa" in ticket.description.lower():
                ticket.description = "Yêu cầu được tiếp nhận để bộ phận phụ trách xử lý và phản hồi."
        if not db.scalar(select(SupportTicket.id).where(SupportTicket.code == "ST-NEU1001")):
            # Preserve compatibility if a previous database still has the old seeded record.
            legacy_first = db.scalar(select(SupportTicket).where(SupportTicket.code == "ST-DEMO1001"))
            if legacy_first:
                legacy_first.code = "ST-NEU1001"
            else:
                db.add(SupportTicket(code="ST-NEU1001", owner_id=student_user.id, category="Hồ sơ sinh viên",
                                     subject="Xác nhận thông tin lớp hành chính", description="Em muốn xác nhận lớp hành chính của mình.",
                                     priority="Bình thường", status="Đang xử lý", assignee_id=support_user.id))
        ticket_samples = [
            ("ST-NEU1002", "Tư vấn hồ sơ tuyển sinh", "Tuyển sinh", "Mới tiếp nhận"),
            ("ST-NEU1003", "Xác nhận học phí", "Học phí và tài chính", "Chờ bổ sung thông tin"),
            ("ST-NEU1004", "Xin giấy xác nhận sinh viên", "Giấy tờ và xác nhận", "Đã giải quyết"),
            ("ST-NEU1005", "Không đăng nhập được cổng sinh viên", "Tài khoản và công nghệ", "Đang xử lý"),
            ("ST-NEU1006", "Hỏi lịch đăng ký học phần", "Đào tạo và học tập", "Đã đóng"),
        ]
        for code, subject, category, status in ticket_samples:
            if not db.scalar(select(SupportTicket.id).where(SupportTicket.code == code)):
                db.add(SupportTicket(code=code, owner_id=student_user.id, category=category, subject=subject,
                                     description="Yêu cầu được tiếp nhận để bộ phận phụ trách xử lý và phản hồi.", priority="Bình thường",
                                     status=status, assignee_id=support_user.id if status != "Mới tiếp nhận" else None))
        for question, answer, category in FAQ_DATA:
            existing_faq = db.scalar(select(FAQ).where(FAQ.question == question))
            if existing_faq:
                existing_faq.answer = answer
                existing_faq.category = category
            else:
                db.add(FAQ(question=question, answer=answer, category=category, is_published=True))
        seed_academic_news(db)
        lecturer_account = users.get("lecturer@neu.local")
        first_lecturer = db.scalar(select(Personnel).where(Personnel.code == "GV-NEU-001"))
        if lecturer_account and first_lecturer and not first_lecturer.user_id and not db.scalar(select(Personnel.id).where(Personnel.user_id == lecturer_account.id)):
            first_lecturer.user_id = lecturer_account.id
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
