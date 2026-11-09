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

LOCAL_TZ = timezone(timedelta(hours=7))
NEWS_DATA = [
    ("khoa-bat-dong-san-70-nam", "Khoa Bất động sản và Kinh tế tài nguyên kỷ niệm 70 năm thành lập", "70 năm NEU", "Lễ kỷ niệm ngày 07/11/2026 nhìn lại hành trình từ ngành Kinh tế Nông nghiệp và các bước phát triển đào tạo của Khoa.", "Ngày 07/11/2026, Đại học Kinh tế Quốc dân tổ chức Lễ kỷ niệm 70 năm thành lập Khoa Bất động sản và Kinh tế tài nguyên (1956–2026). Khoa hiện đảm nhận 5 ngành học với 7 chương trình đại học, 4 chương trình thạc sĩ và 2 chương trình tiến sĩ. Tại buổi lễ, Khoa giới thiệu hai chương trình chất lượng cao bằng tiếng Anh: Kinh doanh Bất động sản và Kinh doanh Chuỗi giá trị Nông sản thực phẩm bền vững.", "https://neu.edu.vn/wp-content/uploads/2026/11/DSC_4281-Copy.webp", datetime(2026, 11, 7, 12, tzinfo=LOCAL_TZ), "https://neu.edu.vn/khoa-bat-dong-san-va-kinh-te-tai-nguyen-dai-hoc-kinh-te-quoc-dan-ky-niem-70-nam-thanh-lap/"),
    ("doi-moi-quan-tri-phat-trien-doi-ngu-neu", "NEU trao đổi về phát triển đội ngũ và đổi mới quản trị đại học", "Hoạt động đào tạo", "Tọa đàm ngày 05/11/2026 nằm trong chuỗi hoạt động kỷ niệm 70 năm, tập trung vào đội ngũ giảng viên, nghiên cứu viên và cán bộ quản lý.", "Sáng 05/11/2026, Đại học Kinh tế Quốc dân tổ chức tọa đàm về xây dựng đội ngũ giảng viên, nghiên cứu viên và cán bộ quản lý giáo dục trong bối cảnh đổi mới toàn diện giáo dục đại học, kết hợp gặp mặt truyền thống các thế hệ viên chức làm công tác tổ chức cán bộ. Chương trình thuộc chuỗi hoạt động kỷ niệm 70 năm thành lập Đại học (1956–2026).", "https://neu.edu.vn/wp-content/uploads/2026/11/DSC_3935-Copy.webp", datetime(2026, 11, 6, 12, tzinfo=LOCAL_TZ), "https://neu.edu.vn/dai-hoc-kinh-te-quoc-dan-phat-trien-doi-ngu-nhan-luc-doi-moi-quan-tri-dai-hoc-trong-giai-doan-moi/"),
    ("hop-tac-neu-thanh-hoa-giao-duc-so", "NEU và Đại học Thanh Hoa thúc đẩy hợp tác giáo dục trực tuyến", "Hợp tác quốc tế", "Hai đại học trao đổi về giáo dục trực tuyến, ứng dụng AI trong giảng dạy và chuyển đổi số trong giáo dục đại học.", "Ngày 03/11/2026, Đại học Kinh tế Quốc dân đón tiếp đoàn công tác Đại học Thanh Hoa do GS. Peng Gang, Phó Giám đốc Đại học Thanh Hoa, dẫn đầu. Buổi làm việc tiếp nối thỏa thuận hợp tác giáo dục ký kết tháng 3/2025; hai bên trao đổi cơ hội hợp tác về giáo dục trực tuyến, ứng dụng trí tuệ nhân tạo trong giảng dạy và chuyển đổi số.", "https://neu.edu.vn/wp-content/uploads/2026/11/DSC_3883-Copy.webp", datetime(2026, 11, 3, 12, tzinfo=LOCAL_TZ), "https://neu.edu.vn/dai-hoc-kinh-te-quoc-dan-va-dai-hoc-thanh-hoa-thuc-day-hop-tac-giao-duc-truc-tuyen-va-chuyen-doi-so-trong-dao-tao/"),
    ("hoi-thao-cac-van-de-duong-dai-trong-phat-trien", "NEU tổ chức Hội thảo khoa học quốc gia về các vấn đề đương đại trong phát triển", "Nghiên cứu khoa học", "Hội thảo ngày 02/11/2026 do NEU phối hợp với Ủy ban Kinh tế và Tài chính tổ chức.", "Chiều 02/11/2026, Đại học Kinh tế Quốc dân phối hợp với Ủy ban Kinh tế và Tài chính tổ chức Hội thảo khoa học quốc gia với chủ đề “Các vấn đề đương đại trong phát triển”. Chương trình có sự tham dự của đại diện cơ quan trung ương, địa phương, chuyên gia, nhà khoa học, cán bộ giảng viên và sinh viên.", "https://neu.edu.vn/wp-content/uploads/2026/11/DSC_3806-Copy.webp", datetime(2026, 11, 2, 12, tzinfo=LOCAL_TZ), "https://neu.edu.vn/hoi-thao-khoa-hoc-quoc-gia-cac-van-de-duong-dai-trong-phat-trien/"),
    ("khoa-thong-ke-70-nam", "Khoa Thống kê kỷ niệm 70 năm: Một cội nguồn – Vạn dặm tương lai", "70 năm NEU", "Lễ kỷ niệm ngày 01/11/2026 nhìn lại đóng góp đào tạo nhân lực thống kê và định hướng đổi mới trong kỷ nguyên dữ liệu.", "Ngày 01/11/2026, Đại học Kinh tế Quốc dân tổ chức Lễ kỷ niệm 70 năm thành lập Khoa Thống kê (1956–2026). Với chủ đề “Một cội nguồn – Vạn dặm tương lai”, sự kiện là dịp nhìn lại truyền thống đào tạo nhiều thế hệ nhân lực thống kê và khẳng định định hướng đổi mới, hội nhập của Khoa trong kỷ nguyên dữ liệu.", "https://neu.edu.vn/wp-content/uploads/2026/11/DSC_3092-Copy.webp", datetime(2026, 11, 1, 12, tzinfo=LOCAL_TZ), "https://neu.edu.vn/khoa-thong-ke-dai-hoc-kinh-te-quoc-dan-70-nam-kien-tao-tri-thuc-doi-moi-trong-ky-nguyen-du-lieu/"),
    ("neu-chao-don-nghien-cuu-sinh-khoa-47", "NEU chào đón 165 nghiên cứu sinh khóa 47 và trao bằng cho 74 tân tiến sĩ", "Hoạt động đào tạo", "Lễ khai giảng nghiên cứu sinh và trao bằng tiến sĩ năm 2026 diễn ra ngày 01/11/2026.", "Chiều 01/11/2026, Đại học Kinh tế Quốc dân tổ chức Lễ khai giảng nghiên cứu sinh khóa 47 và trao bằng tiến sĩ năm 2026. Buổi lễ chào đón 165 tân nghiên cứu sinh và ghi nhận thành quả của 74 tân tiến sĩ.", "https://neu.edu.vn/wp-content/uploads/2026/11/DSC_3388-Copy.webp", datetime(2026, 11, 2, 12, tzinfo=LOCAL_TZ), "https://neu.edu.vn/dai-hoc-kinh-te-quoc-dan-chao-don-165-tan-nghien-cuu-sinh-khoa-47-va-trao-bang-cho-74-tan-tien-si-nam-2026/"),
    ("khoa-qtkd-70-nam", "Khoa Quản trị kinh doanh kỷ niệm 70 năm thành lập", "70 năm NEU", "Dấu mốc 1956–2026 tôn vinh đóng góp của các thế hệ cán bộ, giảng viên, người học và mở ra chặng đường phát triển mới.", "Ngày 31/10/2026, Đại học Kinh tế Quốc dân tổ chức Lễ kỷ niệm 70 năm thành lập Khoa Quản trị kinh doanh (1956–2026). Sự kiện ghi dấu chặng đường xây dựng và phát triển của Khoa, đồng thời tôn vinh đóng góp của các thế hệ cán bộ, giảng viên và người học.", "https://neu.edu.vn/wp-content/uploads/2026/11/DSC_2550-Copy.webp", datetime(2026, 10, 31, 12, tzinfo=LOCAL_TZ), "https://neu.edu.vn/khoa-quan-tri-kinh-doanh-dai-hoc-kinh-te-quoc-dan-ky-niem-70-nam-thanh-lap-dau-an-mot-hanh-trinh/"),
    ("khoi-dong-chuoi-su-kien-70-nam-neu", "NEU khởi động chuỗi sự kiện kỷ niệm 70 năm và công bố bộ nhận diện mới", "70 năm NEU", "Sự kiện ngày 25/01/2026 khởi động chuỗi hoạt động chào mừng dấu mốc 70 năm xây dựng và phát triển.", "Sáng 25/01/2026, Đại học Kinh tế Quốc dân khởi động chuỗi sự kiện kỷ niệm 70 năm thành lập và công bố bộ nhận diện thương hiệu mới. Chương trình mở đầu cho các hoạt động kết nối cộng đồng NEU qua nhiều thế hệ, hướng tới dấu mốc 1956–2026.", "https://neu.edu.vn/wp-content/uploads/2026/01/DSC_4530-Copy.webp", datetime(2026, 1, 25, 12, tzinfo=LOCAL_TZ), "https://dec.neu.edu.vn/khoi-dong-chuoi-su-kien-ky-niem-70-nam-thanh-lap-va-cong-bo-bo-nhan-dien-thuong-hieu-dai-hoc-kinh-te-quoc-dan"),
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

    for slug, title, category, summary, content, image_url, published_at, source_url in NEWS_DATA:
        if not db.scalar(select(NewsArticle.id).where(NewsArticle.slug == slug)):
            db.add(NewsArticle(
                slug=slug, title=title, category=category, summary=summary, content=content,
                image_url=image_url, source_url=source_url, published_at=published_at, status="published",
            ))
    official_events = [
        ("Khởi động chuỗi sự kiện kỷ niệm 70 năm thành lập và công bố bộ nhận diện thương hiệu mới",
         "70 năm NEU", "Sự kiện ngày 25/01/2026 mở đầu chuỗi hoạt động kỷ niệm 70 năm Đại học Kinh tế Quốc dân (1956–2026).",
         datetime(2026, 1, 25, 0, 0, tzinfo=LOCAL_TZ), datetime(2026, 1, 26, 0, 0, tzinfo=LOCAL_TZ), True,
         "https://dec.neu.edu.vn/khoi-dong-chuoi-su-kien-ky-niem-70-nam-thanh-lap-va-cong-bo-bo-nhan-dien-thuong-hieu-dai-hoc-kinh-te-quoc-dan"),
        ("Khoa Quản trị kinh doanh kỷ niệm 70 năm thành lập",
         "70 năm NEU", "Lễ kỷ niệm 70 năm thành lập Khoa Quản trị kinh doanh, giai đoạn 1956–2026.",
         datetime(2026, 10, 31, 0, 0, tzinfo=LOCAL_TZ), datetime(2026, 11, 1, 0, 0, tzinfo=LOCAL_TZ), True,
         "https://neu.edu.vn/khoa-quan-tri-kinh-doanh-dai-hoc-kinh-te-quoc-dan-ky-niem-70-nam-thanh-lap-dau-an-mot-hanh-trinh/"),
        ("Khoa Thống kê kỷ niệm 70 năm thành lập",
         "70 năm NEU", "Lễ kỷ niệm 70 năm thành lập Khoa Thống kê với chủ đề “Một cội nguồn – Vạn dặm tương lai”.",
         datetime(2026, 11, 1, 0, 0, tzinfo=LOCAL_TZ), datetime(2026, 11, 2, 0, 0, tzinfo=LOCAL_TZ), True,
         "https://neu.edu.vn/khoa-thong-ke-dai-hoc-kinh-te-quoc-dan-70-nam-kien-tao-tri-thuc-doi-moi-trong-ky-nguyen-du-lieu/"),
        ("Khoa Bất động sản và Kinh tế tài nguyên kỷ niệm 70 năm thành lập",
         "70 năm NEU", "Lễ kỷ niệm 70 năm thành lập Khoa Bất động sản và Kinh tế tài nguyên (1956–2026).",
         datetime(2026, 11, 7, 0, 0, tzinfo=LOCAL_TZ), datetime(2026, 11, 8, 0, 0, tzinfo=LOCAL_TZ), True,
         "https://neu.edu.vn/khoa-bat-dong-san-va-kinh-te-tai-nguyen-dai-hoc-kinh-te-quoc-dan-ky-niem-70-nam-thanh-lap/"),
        ("Lễ kỷ niệm 70 năm thành lập Đại học Kinh tế Quốc dân (1956–2026) và đón nhận Huân chương Lao động hạng Nhất",
         "70 năm NEU", "Sự kiện chính thức ngày 11/11/2026. Trang sự kiện NEU công bố thời gian 08:30–23:00; chưa nêu địa điểm trên trang.",
         datetime(2026, 11, 11, 8, 30, tzinfo=LOCAL_TZ), datetime(2026, 11, 11, 23, 0, tzinfo=LOCAL_TZ), False,
         "https://neu.edu.vn/su-kien/le-ky-niem-70-nam-thanh-lap-dai-hoc-kinh-te-quoc-dan-1956-2026-va-don-nhan-huan-chuong-lao-dong-hang-nhat/"),
    ]
    for title, category, summary, starts_at, ends_at, is_all_day, source_url in official_events:
        if not db.scalar(select(UniversityEvent.id).where(UniversityEvent.title == title)):
            db.add(UniversityEvent(title=title, category=category, summary=summary, location="",
                                   starts_at=starts_at, ends_at=ends_at, is_all_day=is_all_day,
                                   source_url=source_url, status="published"))


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
