# Tổng quan dự án

## Mục tiêu và phạm vi

Ứng dụng web mô phỏng hệ thống quản lý đại học mang thương hiệu NEU. Các miền source: tuyển sinh, hồ sơ sinh viên, nhân sự/giảng viên, hỗ trợ, thời khóa biểu mẫu, tin tức/thông báo và Study AI Assistant. Không đồng nhất giao diện NEU với dữ liệu chính thức của NEU: danh mục ngành, mức phí, chỉ tiêu, tài khoản và lịch seed được đánh dấu demo trong code.

## Actor

`super_admin`, `student`, `applicant`, `lecturer`, `admission_staff`, `support_staff`, `hr_staff`, `academic_staff`, và khách Guest Chat. Xem [ma trận quyền](09_ROLE_PERMISSION_MATRIX.md).

## Trạng thái chức năng

- `IMPLEMENTED`: API và UI hiện diện cho đăng nhập, dashboard, tuyển sinh CRUD/review theo vai trò, hồ sơ sinh viên, nhân sự, support ticket, notification, Guest/auth chat, FAQ/knowledge admin, lịch sinh viên/giảng viên.
- `PARTIAL`: lịch giảng dạy chỉ đọc từ seed CourseOffering; nội dung ngành/học phí mẫu; AI phụ thuộc API key và provider ngoài.
- `NOT_IMPLEMENTED`: đăng ký tín chỉ, GPA/bảng điểm chính thức, chỉnh sửa/phê duyệt lịch, chấm công/lương, thanh toán thực, đồng bộ dữ liệu NEU thật.
- `UNVERIFIED`: triển khai production, backup/restore, chính sách lưu trữ/xóa guest session.

Trạng thái trên là phân loại source, không khẳng định đã nghiệm thu nghiệp vụ. Chi tiết tại [business requirements](02_BUSINESS_REQUIREMENTS.md) và [limitations](19_KNOWN_ISSUES_AND_LIMITATIONS.md).
