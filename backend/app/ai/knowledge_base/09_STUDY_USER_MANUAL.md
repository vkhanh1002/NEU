---
title: "Hướng dẫn sử dụng hệ thống Study theo vai trò"
document_id: "STUDY-KB-009"
category: "Study System"
language: "vi"
version: "1.0"
status: "draft"
created_at: "2026-10-31"
last_updated: "2026-10-31"
source_type: "system_documentation"
scope: "Chỉ các luồng được xác nhận trong source code hiện tại."
---

# Đăng nhập và quyền

Đăng nhập bằng tài khoản do hệ thống cấp; không chia sẻ mật khẩu/OTP. Sidebar thay đổi theo vai trò. Nếu thấy 403, không cố truy cập URL trực tiếp; liên hệ quản trị viên. Mật khẩu demo chỉ dành cho môi trường thử nghiệm.

## Thí sinh/khách

Có thể xem danh mục ngành và dùng luồng nộp hồ sơ tuyển sinh được bật. Danh sách và trạng thái hồ sơ nội bộ được hạn chế theo vai trò. Một số bước tài khoản/đăng ký ngoài hệ thống chưa có trong MVP; làm theo cổng chính thức của cơ sở tuyển sinh.

## Sinh viên

- **Hồ sơ sinh viên:** xem hồ sơ gắn với tài khoản; cập nhật điện thoại, địa chỉ, giới tính và liên hệ khẩn cấp khi API cho phép. Không có luồng tự sửa email/mã/điểm/ngành.
- **Trung tâm hỗ trợ:** tạo yêu cầu, chọn danh mục, đính kèm file theo giới hạn, theo dõi trao đổi/trạng thái, phản hồi và đánh giá.
- **Study AI:** chat và xem lịch sử riêng của tài khoản. AI không thực hiện thay đổi dữ liệu.

Study chưa có giao diện đăng ký tín chỉ, xem GPA/bảng điểm, công nợ, lịch học, lịch thi, ký túc xá hay cổng học bổng.

## Nhân viên hỗ trợ

Queue hỗ trợ cho phép tìm mã/tên/nội dung, lọc danh mục/trạng thái, mở chi tiết, phản hồi, phân công và cập nhật trạng thái. Chỉ xử lý dữ liệu phục vụ yêu cầu; không tải tệp nếu không cần.

## Super Admin

Quản lý hồ sơ sinh viên, danh mục nhân sự, kho tri thức và FAQ theo quyền. Kho tri thức nhận PDF/DOCX/TXT; Markdown `.md` cũng dùng được sau cập nhật phiên bản này. Tài liệu hiển thị trạng thái xử lý; chỉ tài liệu `ready` được truy xuất. Không tải dữ liệu cá nhân thật vào kho chung.

## Chức năng chưa triển khai

Quản lý tài khoản/phân quyền chi tiết, chỉnh sửa danh mục ngành toàn diện, kỳ tuyển sinh riêng, lịch sử hội thoại quản trị, xóa tài liệu knowledge qua UI, học vụ/GPA/tín chỉ, chấm công/lương, SSO, và truy cập tự phục vụ của nhân sự. Không hướng dẫn thao tác với chức năng chưa có.

**Từ khóa:** đăng nhập Study, hồ sơ, trợ lý, kho tri thức, FAQ, quản trị, quyền truy cập.
