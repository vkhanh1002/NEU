---
title: "FAQ về ứng dụng chat NEU AI của dự án"
institution: "Ứng dụng NEU AI trong repository Study"
category: "faq_chatbot"
source_status: "repository_ui_verified_demo_boundary"
year: 2026
language: "vi"
document_type: "application_user_guide"
---

# Câu hỏi thường gặp về chatbot NEU AI trong dự án

## Chatbot này có phải cổng chat chính thức do NEU phát hành không?

Tài liệu source hiện tại xác nhận đây là một ứng dụng trong repository dự án. Chưa có căn cứ cho thấy nó là cổng chính thức hoặc đã được NEU công bố. Muốn dùng thông tin chính thức, mở website/cổng của Đại học.

## Có thể hỏi những gì?

Giao diện gợi ý câu hỏi về ngành, tuyển sinh và hướng dẫn trong tài liệu công khai. Người dùng có thể đặt câu hỏi tự nhiên; nên nêu năm tuyển sinh, khóa học, chương trình/ngành và đối tượng để tránh trả lời nhầm.

## Chatbot có thể xem điểm, lịch học hoặc hồ sơ cá nhân không?

Giao diện ứng dụng có khu vực hồ sơ/dịch vụ theo tài khoản, nhưng dữ liệu phụ thuộc hồ sơ đã liên kết và môi trường đang chạy. Không coi câu trả lời là dữ liệu chính thức cá nhân. Kiểm tra trực tiếp cổng NEU có thẩm quyền và không gửi mật khẩu/OTP vào chat.

## Vì sao câu trả lời có thể kèm nguồn nhưng vẫn cần kiểm tra?

Giao diện hỗ trợ hiển thị nguồn tham khảo, nhưng nguồn có thể cũ, không áp dụng đúng khóa/năm hoặc chưa đủ để trả lời toàn bộ câu hỏi. Mở nguồn gốc, xác nhận ngày và phạm vi trước khi ra quyết định.

## Tôi muốn bắt đầu cuộc trò chuyện mới hoặc xóa lịch sử thì làm sao?

Trong khung chat công khai hiện tại có thao tác tạo cuộc trò chuyện mới và xóa lịch sử. Trang trợ lý đăng nhập còn quản lý danh sách cuộc trò chuyện. Nếu bản đang chạy khác giao diện, dùng nút tương ứng trên giao diện hiện tại.

## Tôi có thể nạp tài liệu vào Kho tri thức không?

Kho tri thức trong bản repository dành cho vai trò quản trị cấp cao. Người quản trị có thể nạp tài liệu và FAQ qua trang quản trị. File được tải lên cần qua kiểm tra nội dung và trạng thái; việc upload không đồng nghĩa tài liệu đã được public hoặc hệ thống đã trả lời đúng.

## Nếu chatbot trả lời về học phí hoặc thủ tục mà không có nguồn thì sao?

Không dùng câu trả lời đó làm căn cứ. Tra trang tuyển sinh/quy chế/OneGate/Thông báo chính thức của NEU. Nếu tài liệu hiện có chưa xác minh nội dung, câu trả lời an toàn là nêu thiếu nguồn và dẫn đúng cổng.

### Nguồn kiểm tra nội bộ dự án

| Thành phần giao diện | Đường dẫn trong repository | Phạm vi kiểm tra |
|---|---|---|
| Chat công khai | `frontend/features/guest-chat.tsx` | Giao diện guest, lịch sử và thao tác cơ bản |
| Trợ lý đăng nhập | `frontend/features/assistant.tsx` | Lịch sử, trạng thái và nguồn trong tin nhắn |
| Kho tri thức | `frontend/features/knowledge-admin.tsx` | Upload tài liệu và FAQ |

Giao diện dự án không phải nguồn xác nhận hệ thống NEU chính thức.
