# Chính sách cập nhật Knowledge Base NEU

## Chu kỳ và ưu tiên

- Trước mỗi mùa tuyển sinh, thay bộ hồ sơ năm cũ bằng tài liệu riêng của năm mới sau khi có thông báo/quyết định chính thức. Giữ bản 2026 để tra cứu lịch sử.
- Rà lại học phí, miễn giảm, học bổng ít nhất mỗi năm học và khi NEU công bố quyết định mới.
- Rà lại liên kết cổng sinh viên, OneGate, chương trình đào tạo, cơ cấu và đầu mối liên hệ định kỳ; nguồn trang web có thể thay đổi.
- Nội dung app chỉ cập nhật khi source code trong repository đổi. Ghi rõ ngày khảo sát và các tệp đã kiểm tra.

## Quy tắc biên tập

1. Mỗi tài liệu có tiêu đề rõ, phạm vi/năm/đối tượng, trạng thái nguồn nếu phù hợp, ngày rà soát và bảng nguồn tham khảo.
2. Ưu tiên quyết định/thông báo NEU, trang tuyển sinh NEU, cổng chương trình NEU, và đơn vị NEU chịu trách nhiệm nội dung.
3. Nếu thông tin có mâu thuẫn, không tự chọn số liệu thuận tiện; kiểm tra văn bản mới hơn/đính chính và ghi chú xung đột cho đến khi xác minh.
4. Không suy diễn từ seed code, nội dung demo, hoặc bài tư vấn không chính thức thành chính sách của trường.
5. Khi chuyển nguồn thành dữ liệu có cấu trúc, giữ mã ngành, năm/khóa, đơn vị, đơn vị tính và điều kiện đi kèm.
6. Không đưa thông tin cá nhân, bí mật, API key, dữ liệu đăng nhập hay hồ sơ sinh viên lên Knowledge Base.

## Quy trình phát hành trong ứng dụng

1. Biên tập và rà nguồn trong repository; giữ câu chữ an toàn cho năm/đối tượng.
2. Quản trị viên upload đúng các tệp trong `knowledge_base/`. README và `knowledge_base_internal/` là tài liệu quản trị, không upload làm nguồn chatbot.
3. Xác nhận hệ thống đã xử lý tài liệu, số lượng/trạng thái đúng và nội dung xem trước không lỗi mã hóa.
4. Kiểm tra một nhóm câu hỏi từ `question_catalog.md`, đặc biệt câu hỏi có năm, câu so sánh và câu ngoài phạm vi.
5. Chỉ public/duyệt sau khi xác nhận nội dung, nguồn trích dẫn và câu trả lời. Theo dõi trong giao diện quản trị.

Việc thay đổi Markdown không tự đồng nghĩa tài liệu đã được upload, xử lý, duyệt hoặc public trong database.
