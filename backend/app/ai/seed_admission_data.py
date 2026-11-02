import json
import logging
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models import (
    AdmissionProgram, AdmissionScore, Department, FAQ, FaqItem,
    KnowledgeChunk, KnowledgeDocument, TuitionFee, User
)

logger = logging.getLogger(__name__)

DEPARTMENTS_DATA = [
    {
        "name": "Phòng Quản lý Đào tạo",
        "code": "QLDT",
        "description": "Phụ trách kế hoạch học tập, thời khóa biểu, đăng ký tín chỉ, xét tốt nghiệp, chuyển ngành, bảo lưu kết quả học tập.",
        "email": "qldt@neu.edu.vn",
        "phone": "024.3628.0280 (máy lẻ 5656, 5658)",
        "location": "Phòng 210, Tòa nhà A1 (Tòa nhà Thế kỷ), 207 Giải Phóng, Hà Nội",
        "office_hours": "Thứ 2 - Thứ 6: 08:00 - 11:30 & 13:30 - 17:00",
    },
    {
        "name": "Phòng Quản lý Đón tiếp & Tuyển sinh",
        "code": "TS",
        "description": "Tư vấn tuyển sinh đại học chính quy, liên thông, văn bằng 2, thạc sĩ, tiến sĩ, tiếp nhận hồ sơ xét tuyển và hướng dẫn nhập học.",
        "email": "tuyensinh@neu.edu.vn",
        "phone": "024.3628.0280 (máy lẻ 5111, 5112, 5113) - Hotline: 0888.128.558",
        "location": "Phòng 102, Tòa nhà A1, 207 Giải Phóng, Hà Nội",
        "office_hours": "Thứ 2 - Thứ 6: 08:00 - 17:00 (Mùa tuyển sinh trực cả Thứ 7)",
    },
    {
        "name": "Phòng Tài chính - Kế toán",
        "code": "TCKT",
        "description": "Thu học phí, giải quyết chính sách miễn giảm học phí, chi trả học bổng khuyến khích học tập và các thủ tục công nợ sinh viên.",
        "email": "tckt@neu.edu.vn",
        "phone": "024.3628.0280 (máy lẻ 5333, 5335)",
        "location": "Phòng 109, Tòa nhà A1, 207 Giải Phóng, Hà Nội",
        "office_hours": "Thứ 2 - Thứ 6: 08:00 - 11:30 & 13:30 - 16:30",
    },
    {
        "name": "Phòng Công tác Chính trị & Quản lý Sinh viên",
        "code": "CTCT_QLSV",
        "description": "Cấp giấy xác nhận sinh viên, cấp lại thẻ sinh viên, giải quyết chế độ chính sách sinh viên, khen thưởng - kỷ luật, quản lý hồ sơ sinh viên.",
        "email": "ctct.qlsv@neu.edu.vn",
        "phone": "024.3628.0280 (máy lẻ 5444, 5445)",
        "location": "Phòng 105, Tòa nhà A1, 207 Giải Phóng, Hà Nội",
        "office_hours": "Thứ 2 - Thứ 6: 08:00 - 11:30 & 13:30 - 17:00",
    },
    {
        "name": "Ban Quản lý Ký túc xá",
        "code": "KTX",
        "description": "Tiếp nhận đăng ký nội trú, quản lý an ninh trật tự, cơ sở vật chất phòng ở ký túc xá sinh viên trong khuôn viên trường.",
        "email": "ktx@neu.edu.vn",
        "phone": "024.3869.4188",
        "location": "Tòa nhà Ký túc xá NEU, Cổng phụ đường Trần Đại Nghĩa, Hà Nội",
        "office_hours": "Thứ 2 - Thứ 7: 07:30 - 17:30 (Trực ban 24/7)",
    },
    {
        "name": "Trung tâm Thư viện Phạm Văn Đồng",
        "code": "LIB",
        "description": "Mượn trả sách, cung cấp tài liệu nghiên cứu, cấp tài khoản tra cứu cơ sở dữ liệu quốc tế, không gian tự học và phòng thảo luận nhóm.",
        "email": "thuvien@neu.edu.vn",
        "phone": "024.3628.0280 (máy lẻ 5888)",
        "location": "Tòa nhà Thư viện Phạm Văn Đồng (cạnh Tòa nhà A1), 207 Giải Phóng",
        "office_hours": "Thứ 2 - Thứ 7: 07:30 - 21:00, Chủ nhật: 08:00 - 17:00",
    },
    {
        "name": "Trung tâm Ứng dụng CNTT (Phụ trách Hệ thống mạng & Cổng thông tin)",
        "code": "CNTT",
        "description": "Cấp lại mật khẩu tài khoản học vụ portal sinh viên, email NEU Office 365, hỗ trợ kỹ thuật đăng ký học trực tuyến.",
        "email": "cntt@neu.edu.vn",
        "phone": "024.3628.0280 (máy lẻ 5999)",
        "location": "Phòng 301, Tòa nhà A1, 207 Giải Phóng, Hà Nội",
        "office_hours": "Thứ 2 - Thứ 6: 08:00 - 17:00",
    },
]

PROGRAMS_2026 = [
    {
        "major_code": "7340101",
        "name": "Quản trị kinh doanh",
        "program_type": "Chuẩn",
        "quota": 320,
        "methods": ["THPT", "KetHopIELTS", "DGNL_HSA", "DGTD_TSA", "TuyenThang"],
        "subject_groups": "A00, A01, D01, D07",
        "year": 2026,
        "note": "Ngành truyền thống thế mạnh hàng đầu NEU. Đào tạo nhà quản trị chiến lược, marketing, nhân sự.",
    },
    {
        "major_code": "7340201",
        "name": "Tài chính - Ngân hàng",
        "program_type": "Chuẩn",
        "quota": 450,
        "methods": ["THPT", "KetHopIELTS", "DGNL_HSA", "DGTD_TSA", "TuyenThang"],
        "subject_groups": "A00, A01, D01, D07",
        "year": 2026,
        "note": "Đào tạo chuyên sâu ngân hàng số, đầu tư tài chính, chứng khoán, quản trị rủi ro.",
    },
    {
        "major_code": "7340301",
        "name": "Kế toán",
        "program_type": "Chuẩn",
        "quota": 380,
        "methods": ["THPT", "KetHopIELTS", "DGNL_HSA", "DGTD_TSA", "TuyenThang"],
        "subject_groups": "A00, A01, D01, D07",
        "year": 2026,
        "note": "Tích hợp chứng chỉ quốc tế ACCA/CPA, cơ hội làm việc tại Big4 kiểm toán toàn cầu.",
    },
    {
        "major_code": "7340302",
        "name": "Kiểm toán",
        "program_type": "Chuẩn",
        "quota": 220,
        "methods": ["THPT", "KetHopIELTS", "DGNL_HSA", "DGTD_TSA", "TuyenThang"],
        "subject_groups": "A00, A01, D01, D07",
        "year": 2026,
        "note": "Ngành có điểm chuẩn cao bậc nhất NEU. Tỉ lệ sinh viên có việc làm trước khi tốt nghiệp đạt 98%.",
    },
    {
        "major_code": "7340115",
        "name": "Logistics và Quản lý chuỗi cung ứng",
        "program_type": "Chuẩn",
        "quota": 180,
        "methods": ["THPT", "KetHopIELTS", "DGNL_HSA", "DGTD_TSA", "TuyenThang"],
        "subject_groups": "A00, A01, D01, D07",
        "year": 2026,
        "note": "Ngành cực hot có điểm chuẩn top 1 NEU liên tục nhiều năm. Nhu cầu nhân lực quốc tế lớn.",
    },
    {
        "major_code": "7340116",
        "name": "Kinh doanh quốc tế",
        "program_type": "Chuẩn",
        "quota": 210,
        "methods": ["THPT", "KetHopIELTS", "DGNL_HSA", "DGTD_TSA", "TuyenThang"],
        "subject_groups": "A00, A01, D01, D07",
        "year": 2026,
        "note": "Điểm chuẩn nhóm đầu, đào tạo thương mại điện tử quốc tế, đầu tư xuất nhập khẩu.",
    },
    {
        "major_code": "7340120",
        "name": "Marketing (Quản trị Marketing)",
        "program_type": "Chuẩn",
        "quota": 250,
        "methods": ["THPT", "KetHopIELTS", "DGNL_HSA", "DGTD_TSA", "TuyenThang"],
        "subject_groups": "A00, A01, D01, D07",
        "year": 2026,
        "note": "Ngành sáng tạo, truyền thông số, thương hiệu và tiếp thị đa kênh.",
    },
    {
        "major_code": "7480201",
        "name": "Công nghệ thông tin",
        "program_type": "Chuẩn",
        "quota": 150,
        "methods": ["THPT", "KetHopIELTS", "DGNL_HSA", "DGTD_TSA", "TuyenThang"],
        "subject_groups": "A00, A01, D01, D07",
        "year": 2026,
        "note": "Ứng dụng CNTT trong kinh tế, tài chính ngân hàng, bảo mật và kỹ thuật phần mềm.",
    },
    {
        "major_code": "7480108",
        "name": "Khoa học dữ liệu trong Kinh tế & Kinh doanh (DSEB)",
        "program_type": "Tiên tiến",
        "quota": 100,
        "methods": ["KetHopIELTS", "DGNL_HSA", "DGTD_TSA", "TuyenThang", "THPT"],
        "subject_groups": "A00, A01, D01, D07",
        "year": 2026,
        "note": "Dạy hoàn toàn bằng tiếng Anh, chuyên sâu Data Science, Machine Learning, Big Data Analytics.",
    },
    {
        "major_code": "7480107",
        "name": "Trí tuệ nhân tạo (AI) trong Kinh doanh",
        "program_type": "Tiên tiến",
        "quota": 80,
        "methods": ["KetHopIELTS", "DGNL_HSA", "DGTD_TSA", "TuyenThang", "THPT"],
        "subject_groups": "A00, A01, D01, D07",
        "year": 2026,
        "note": "Chương trình mới định hướng ứng dụng GenAI, LLMs và thuật toán tự động hóa quy trình kinh doanh.",
    },
    {
        "major_code": "7340122",
        "name": "Thương mại điện tử (E-Commerce)",
        "program_type": "Chuẩn",
        "quota": 150,
        "methods": ["THPT", "KetHopIELTS", "DGNL_HSA", "DGTD_TSA", "TuyenThang"],
        "subject_groups": "A00, A01, D01, D07",
        "year": 2026,
        "note": "Kết hợp kinh doanh và công nghệ nền tảng số, thanh toán điện tử.",
    },
    {
        "major_code": "7380101",
        "name": "Luật Kinh tế",
        "program_type": "Chuẩn",
        "quota": 180,
        "methods": ["THPT", "KetHopIELTS", "DGNL_HSA", "DGTD_TSA", "TuyenThang"],
        "subject_groups": "A00, A01, D01, D07",
        "year": 2026,
        "note": "Đào tạo chuyên gia pháp lý doanh nghiệp, giải quyết tranh chấp kinh doanh quốc tế.",
    },
]

SCORES_DATA = [
    # 2025 THPT (Thang 30)
    {"program_code": "7340115", "program_name": "Logistics và Quản lý chuỗi cung ứng", "year": 2025, "method": "Điểm thi THPT", "score": 28.30, "scale": 30, "note": "Tiêu chí phụ: Điểm môn Toán >= 8.8"},
    {"program_code": "7340116", "program_name": "Kinh doanh quốc tế", "year": 2025, "method": "Điểm thi THPT", "score": 28.15, "scale": 30, "note": "Tiêu chí phụ: Điểm môn Toán >= 8.6"},
    {"program_code": "7340120", "program_name": "Marketing", "year": 2025, "method": "Điểm thi THPT", "score": 28.05, "scale": 30, "note": "Tiêu chí phụ: Điểm môn Tiếng Anh >= 9.0"},
    {"program_code": "7340302", "program_name": "Kiểm toán", "year": 2025, "method": "Điểm thi THPT", "score": 28.10, "scale": 30, "note": "Tiêu chí phụ: Điểm môn Toán >= 8.8"},
    {"program_code": "7340101", "program_name": "Quản trị kinh doanh", "year": 2025, "method": "Điểm thi THPT", "score": 27.65, "scale": 30, "note": "Tổ hợp A00, A01, D01"},
    {"program_code": "7340201", "program_name": "Tài chính - Ngân hàng", "year": 2025, "method": "Điểm thi THPT", "score": 27.50, "scale": 30, "note": "Tổ hợp A00, A01, D01, D07"},
    {"program_code": "7480201", "program_name": "Công nghệ thông tin", "year": 2025, "method": "Điểm thi THPT", "score": 27.40, "scale": 30, "note": "Môn Toán hệ số 1"},
    {"program_code": "7340122", "program_name": "Thương mại điện tử", "year": 2025, "method": "Điểm thi THPT", "score": 27.85, "scale": 30, "note": "Tổ hợp A00, A01, D01"},
    {"program_code": "7480108", "program_name": "Khoa học dữ liệu (DSEB)", "year": 2025, "method": "Điểm thi THPT", "score": 27.95, "scale": 30, "note": "Tiêu chí tiếng Anh >= 8.5"},

    # 2025 ĐGNL ĐHQGHN (HSA - Thang 150 quy về thang 30 hoặc xét điểm gốc)
    {"program_code": "7340115", "program_name": "Logistics và Quản lý chuỗi cung ứng", "year": 2025, "method": "ĐGNL HSA (ĐHQGHN)", "score": 115.5, "scale": 150, "note": "Quy đổi theo công thức Đề án NEU"},
    {"program_code": "7340116", "program_name": "Kinh doanh quốc tế", "year": 2025, "method": "ĐGNL HSA (ĐHQGHN)", "score": 114.0, "scale": 150, "note": "Quy đổi theo công thức Đề án NEU"},
    {"program_code": "7340101", "program_name": "Quản trị kinh doanh", "year": 2025, "method": "ĐGNL HSA (ĐHQGHN)", "score": 109.5, "scale": 150, "note": "Quy đổi theo công thức Đề án NEU"},
    {"program_code": "7480201", "program_name": "Công nghệ thông tin", "year": 2025, "method": "ĐGNL HSA (ĐHQGHN)", "score": 108.0, "scale": 150, "note": "Quy đổi theo công thức Đề án NEU"},

    # 2024 THPT (Thang 30)
    {"program_code": "7340115", "program_name": "Logistics và Quản lý chuỗi cung ứng", "year": 2024, "method": "Điểm thi THPT", "score": 28.20, "scale": 30, "note": ""},
    {"program_code": "7340116", "program_name": "Kinh doanh quốc tế", "year": 2024, "method": "Điểm thi THPT", "score": 28.00, "scale": 30, "note": ""},
    {"program_code": "7340120", "program_name": "Marketing", "year": 2024, "method": "Điểm thi THPT", "score": 27.90, "scale": 30, "note": ""},
    {"program_code": "7340302", "program_name": "Kiểm toán", "year": 2024, "method": "Điểm thi THPT", "score": 28.00, "scale": 30, "note": ""},
    {"program_code": "7340101", "program_name": "Quản trị kinh doanh", "year": 2024, "method": "Điểm thi THPT", "score": 27.45, "scale": 30, "note": ""},
    {"program_code": "7340201", "program_name": "Tài chính - Ngân hàng", "year": 2024, "method": "Điểm thi THPT", "score": 27.35, "scale": 30, "note": ""},
    {"program_code": "7480201", "program_name": "Công nghệ thông tin", "year": 2024, "method": "Điểm thi THPT", "score": 27.15, "scale": 30, "note": ""},
]

TUITION_DATA = [
    {
        "program_code": "CH_CHUAN",
        "program_name": "Chương trình Đại trà (Chuẩn)",
        "cohort": "K65, K66, K67",
        "academic_year": "2025-2026",
        "per_credit_vnd": 680000,
        "per_year_vnd": 22000000,
        "note": "Học phí khoảng 20-25 triệu đồng/năm học (tùy số lượng tín chỉ đăng ký, trung bình 32-35 tín chỉ/năm).",
    },
    {
        "program_code": "CH_CLC",
        "program_name": "Chương trình Chất lượng cao (CLC / AEP)",
        "cohort": "K65, K66, K67",
        "academic_year": "2025-2026",
        "per_credit_vnd": 1450000,
        "per_year_vnd": 45000000,
        "note": "Học phí dao động 40-50 triệu đồng/năm học. Đào tạo tăng cường tiếng Anh, giảng viên đầu ngành.",
    },
    {
        "program_code": "CH_TIEN_TIEN",
        "program_name": "Chương trình Tiên tiến (AEP - Dạy 100% tiếng Anh)",
        "cohort": "K65, K66, K67",
        "academic_year": "2025-2026",
        "per_credit_vnd": 2100000,
        "per_year_vnd": 65000000,
        "note": "Học phí dao động 60-70 triệu đồng/năm học theo chuẩn chương trình các đại học danh tiếng của Mỹ/Anh.",
    },
    {
        "program_code": "CH_POHE",
        "program_name": "Chương trình Định hướng ứng dụng (POHE)",
        "cohort": "K65, K66, K67",
        "academic_year": "2025-2026",
        "per_credit_vnd": 1200000,
        "per_year_vnd": 38000000,
        "note": "Học phí khoảng 35-42 triệu đồng/năm học. Chú trọng thực hành tại doanh nghiệp từ năm 2.",
    },
    {
        "program_code": "CH_IBD",
        "program_name": "Chương trình Cử nhân Quốc tế IBD@NEU (Đại học West of England / Sunderland cấp bằng)",
        "cohort": "K20, K21",
        "academic_year": "2025-2026",
        "per_credit_vnd": 0,
        "per_year_vnd": 95000000,
        "note": "Học phí trọn gói 4 năm khoảng 380 - 450 triệu đồng tùy ngành và lộ trình chuyển tiếp.",
    },
]

FAQ_ITEMS_DATA = [
    {
        "question": "Thí sinh có chứng chỉ IELTS 6.5 trở lên thì được xét tuyển vào NEU theo phương thức nào?",
        "answer": "Thí sinh có chứng chỉ IELTS từ 5.5 trở lên (hoặc TOEFL iBT 46+, TOEIC 4 kỹ năng tương đương) còn hiệu lực tính đến ngày xét tuyển được đăng ký theo Phương thức Xét tuyển kết hợp (Mã phương thức 501 / Nhóm 1 & 2 của NEU). Điểm xét tuyển = Điểm IELTS quy đổi + Điểm 02 môn thi tốt nghiệp THPT (trong đó bắt buộc có môn Toán và 01 môn khác không phải tiếng Anh) + Điểm ưu tiên (nếu có). IELTS 6.5 thường được quy đổi thành 9.0 đến 9.5 điểm tùy đề án cụ thể năm tuyển sinh.",
        "category": "Tuyển sinh",
        "audience": "tuyen_sinh",
    },
    {
        "question": "Thời gian và quy trình nộp hồ sơ xét tuyển sớm tại NEU diễn ra khi nào?",
        "answer": "Hàng năm, NEU mở cổng đăng ký trực tuyến xét tuyển kết hợp sớm (ĐGNL, Chứng chỉ quốc tế SAT/ACT/IELTS) từ khoảng tháng 5 đến tháng 6 trên cổng tuyển sinh https://tuyensinh.neu.edu.vn. Thí sinh đăng ký tài khoản, tải ảnh hồ sơ minh chứng (học bạ, chứng chỉ). Sau khi có kết quả xét tuyển sớm có điều kiện, thí sinh bắt buộc phải đăng ký nguyện vọng lên Cổng thông tin tuyển sinh chung của Bộ GD&ĐT vào tháng 7 để được công nhận trúng tuyển chính thức.",
        "category": "Tuyển sinh",
        "audience": "tuyen_sinh",
    },
    {
        "question": "Quy chế xin hoãn thi hoặc bảo lưu kết quả học tập tại NEU như thế nào?",
        "answer": "Sinh viên có lý do chính đáng (ốm đau nằm viện, hoàn cảnh gia đình đặc biệt, thực hiện nghĩa vụ quân sự...) phải làm đơn gửi Phòng Quản lý Đào tạo (Phòng 210, Nhà A1) kèm hồ sơ minh chứng (giấy ra viện có dấu đỏ của bệnh viện từ cấp quận/huyện trở lên) trước ngày thi hoặc tối đa 03 ngày làm việc sau buổi thi. Trường hợp bảo lưu học kỳ, sinh viên phải hoàn thành ít nhất 01 học kỳ tại trường và không thuộc diện bị buộc thôi học.",
        "category": "Học vụ",
        "audience": "sinh_vien",
    },
    {
        "question": "Thủ tục xin cấp Giấy xác nhận sinh viên để hoãn nghĩa vụ quân sự hoặc vay vốn ngân hàng?",
        "answer": "Sinh viên đăng nhập vào Cổng thông tin sinh viên portal.neu.edu.vn, chọn mục 'Dịch vụ trực tuyến' -> 'Đăng ký giấy xác nhận sinh viên'. Chọn loại giấy (hoãn NVQS, vay vốn NHCSXH, vé xe buýt, giảm thuế). Sau 1-2 ngày làm việc, sinh viên đến nhận trực tiếp tại Phòng Công tác Chính trị & QLSV (Phòng 105, Nhà A1) hoặc đăng ký gửi bản mềm/chuyển phát nhanh.",
        "category": "Thủ tục",
        "audience": "sinh_vien",
    },
    {
        "question": "Điều kiện để sinh viên NEU được đăng ký học vượt hoặc tốt nghiệp sớm?",
        "answer": "Sinh viên có điểm trung bình chung tích lũy (CPA) từ 2.50 trở lên và không bị cảnh cáo học tập được phép đăng ký tối đa đến 25 tín chỉ/học kỳ chính và 8-10 tín chỉ trong học kỳ hè. Khi tích lũy đủ số tín chỉ quy định của ngành (thường từ 128 - 135 tín chỉ), hoàn thành chứng chỉ chuẩn đầu ra Tiếng Anh, Tin học và GDTC/GDQP-AN thì sinh viên được làm thủ tục xét tốt nghiệp đợt sớm (thường tổ chức 3-4 đợt xét tốt nghiệp/năm).",
        "category": "Đào tạo",
        "audience": "sinh_vien",
    },
]


def seed_admission_and_departments(db: Session):
    admin = db.scalars(select(User).where(User.role == "super_admin")).first()
    admin_id = admin.id if admin else "system-admin"

    # Seed Departments
    for d in DEPARTMENTS_DATA:
        existing = db.scalars(select(Department).where(Department.name == d["name"])).first()
        if not existing:
            dept = Department(**d)
            db.add(dept)
    db.commit()

    # Seed Programs
    for p in PROGRAMS_2026:
        existing = db.scalars(select(AdmissionProgram).where(
            AdmissionProgram.major_code == p["major_code"],
            AdmissionProgram.year == p["year"],
            AdmissionProgram.program_type == p["program_type"]
        )).first()
        if not existing:
            prog = AdmissionProgram(**p)
            db.add(prog)
    db.commit()

    # Seed Scores
    for s in SCORES_DATA:
        existing = db.scalars(select(AdmissionScore).where(
            AdmissionScore.program_code == s["program_code"],
            AdmissionScore.year == s["year"],
            AdmissionScore.method == s["method"]
        )).first()
        if not existing:
            score = AdmissionScore(**s)
            db.add(score)
    db.commit()

    # Seed Tuition Fees
    for t in TUITION_DATA:
        existing = db.scalars(select(TuitionFee).where(
            TuitionFee.program_code == t["program_code"],
            TuitionFee.cohort == t["cohort"]
        )).first()
        if not existing:
            fee = TuitionFee(**t)
            db.add(fee)
    db.commit()

    # Seed FAQ Items
    for f in FAQ_ITEMS_DATA:
        existing = db.scalars(select(FaqItem).where(FaqItem.question == f["question"])).first()
        if not existing:
            item = FaqItem(**f)
            db.add(item)
    db.commit()

    logger.info("Successfully seeded structured Admission, Scores, Tuition, Departments, and FAQ items!")


if __name__ == "__main__":
    db = SessionLocal()
    seed_admission_and_departments(db)
    print("Seed finished!")
