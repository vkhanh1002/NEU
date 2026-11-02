---
title: "Hướng dẫn dùng ứng dụng NEU AI trong repository Study"
institution: "Ứng dụng NEU AI của dự án; không phải cổng chính thức NEU"
category: "digital_services"
source_status: "repository_ui_verified_demo_boundary"
year: 2026
language: "vi"
document_type: "application_user_guide"
---

# Hướng dẫn sử dụng ứng dụng NEU AI trong repository

## Phạm vi

Tài liệu này mô tả giao diện có trong repository của dự án NEU AI/Study tại ngày 03/11/2026. Đây là hướng dẫn cho **bản ứng dụng trong dự án**, không phải tuyên bố rằng NEU đã phát hành ứng dụng này như cổng dịch vụ chính thức. Dữ liệu hiển thị có thể là dữ liệu demo hoặc hồ sơ được tạo cho môi trường thử nghiệm; chưa có căn cứ khẳng định hệ thống đồng bộ với các cơ sở dữ liệu thật của NEU.

## Hỏi chatbot

- Nút **Hỏi tư vấn** mở khung tư vấn công khai, không yêu cầu đăng nhập trong giao diện hiện tại.
- Có thể nhập câu hỏi về tuyển sinh, ngành hoặc nguồn tài liệu công khai; giao diện hiển thị nguồn tham khảo khi câu trả lời có nguồn.
- Khung chat có thao tác tạo cuộc trò chuyện mới, xóa lịch sử, phóng to/thu nhỏ và đóng.
- Khi đăng nhập, trang **Trợ lý NEU** có lịch sử/cuộc hội thoại và vùng hiển thị nguồn cho câu trả lời.
- Câu trả lời của AI có thể sai hoặc thiếu. Kiểm tra nguồn gốc, năm và nội dung gốc trước khi dùng cho quyết định quan trọng.

Không nhập mật khẩu, mã OTP hoặc dữ liệu cá nhân nhạy cảm vào cuộc trò chuyện. Khả năng tra cứu hồ sơ phụ thuộc tài khoản và dữ liệu được liên kết; không giả định chatbot truy cập được toàn bộ hồ sơ NEU.

## Các khu vực của ứng dụng

Giao diện repository hiện có các trang/khu vực:

- Tuyển sinh và hồ sơ thí sinh.
- Trợ lý chat, có chế độ công khai và đăng nhập.
- Hồ sơ sinh viên/giảng viên/nhân viên theo quyền ứng dụng.
- Thời khóa biểu, kết quả, lịch thi, tài chính, chuyên cần và bài tập dành cho sinh viên.
- Thời khóa biểu giảng dạy cho giảng viên.
- Yêu cầu hỗ trợ và thông báo.
- Kho tri thức và FAQ dành cho vai trò quản trị cấp cao.

Trang lịch hoặc hồ sơ có thể trống nếu tài khoản thử nghiệm chưa được liên kết dữ liệu. Các trang trong mã nguồn không tự xác nhận NEU có API hoặc hệ thống chính thức tương ứng.

## Quản trị Kho tri thức

Trong ứng dụng, trang Kho tri thức ở đường dẫn `/admin` dành cho vai trò super admin. Giao diện hỗ trợ nạp tài liệu và quản lý FAQ; quyền xóa/đổi trạng thái có thể ảnh hưởng đến nội dung chatbot. Chỉ dùng file đã kiểm tra nguồn, năm, trạng thái và tính công khai. Tải file vào ứng dụng không tự chứng minh mọi phần đã được index/được chatbot truy xuất; cần kiểm tra trạng thái tài liệu và câu trả lời có nguồn trong chính môi trường chạy.

## Chức năng chưa nên giới thiệu như đã có

Trong các route và thành phần giao diện được rà soát không thấy một ứng dụng lập kế hoạch học tập độc lập (Study Planner) hay kết nối SSO/đồng bộ hồ sơ với hệ thống thật của NEU. Không hứa rằng người dùng có thể đăng ký tín chỉ, nộp hồ sơ chính thức, thanh toán, xem dữ liệu NEU live hoặc hoàn tất thủ tục qua bản ứng dụng này trừ khi giao diện và tích hợp đó được xác nhận sau.

### Nguồn kiểm tra nội bộ dự án

| Thành phần giao diện | Đường dẫn trong repository | Nội dung được quan sát |
|---|---|---|
| Sidebar/route và quyền truy cập | `frontend/components/shell.tsx` | Các mục điều hướng và vai trò |
| Chat đăng nhập | `frontend/features/assistant.tsx` | Lịch sử chat, trạng thái provider, nguồn |
| Chat công khai | `frontend/features/guest-chat.tsx` | Giao diện guest, thao tác cuộc trò chuyện, nguồn |
| Kho tri thức | `frontend/features/knowledge-admin.tsx` | Upload tài liệu, FAQ, trạng thái AI |
| Dịch vụ sinh viên | `frontend/features/student-services.tsx` | Lịch, kết quả, thi, tài chính, chuyên cần, bài tập |

Đây là rà soát source code của dự án, không phải nguồn xác nhận dịch vụ của NEU.
