# Nghiệp vụ và yêu cầu đã đối chiếu

## Tuyển sinh — `PARTIAL`

Actor thí sinh và admission staff. Applicant lưu email, họ tên, thông tin liên lạc, ngành mong muốn, phương thức, trạng thái và ghi chú xét duyệt. Backend có endpoint tạo/xem hồ sơ và cập nhật review; kết quả là trạng thái/ghi chú được lưu. Không có bằng chứng workflow kiểm tra chứng từ đầy đủ, chuyển hồ sơ trúng tuyển thành sinh viên tự động hay quy trình tuyển sinh chính thức.

## Hồ sơ sinh viên — `PARTIAL`

Student gắn tùy chọn với User và Applicant; profile API giới hạn trường được phép cập nhật. Student xem lịch, assignments, exams, results, conduct và finance theo hồ sơ gắn tài khoản. Những bản ghi phần lớn seed; không phải bảng điểm hay công nợ chính thức. Đăng ký học phần chưa triển khai.

## Nhân sự/giảng viên — `PARTIAL`

Personnel dùng chung cho `lecturer`/`employee`; giảng viên có thể liên kết User qua `user_id`. Admin quản lý hồ sơ; giảng viên xem lớp được phân công và roster lớp đó. Không có lương, chấm công hoặc quy trình HR.

## Hỗ trợ người học — `IMPLEMENTED` (ticket cơ bản)

Người dùng đăng nhập tạo ticket có category/subject/description; xem/trao đổi/đính kèm/đánh giá theo quyền sở hữu. Nhân viên hỗ trợ xử lý/phân công/cập nhật trạng thái. Không có cam kết SLA.

## Chatbot — `PARTIAL`

Guest session ẩn danh có token; auth chat lưu theo user; RAG, citation, FAQ, gợi ý, rate limit và provider LLM có trong source. Câu trả lời phụ thuộc nguồn/index và key hợp lệ. Xem [AI](12_AI_CHATBOT_ARCHITECTURE.md).
