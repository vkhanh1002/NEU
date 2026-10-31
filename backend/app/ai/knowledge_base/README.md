# Quản trị kho tri thức Study

## Danh mục trong bộ khởi tạo

Thư mục có 14 tài liệu chuyên đề (`00`–`13`), 200 FAQ duy nhất trong `10_UNIVERSITY_FAQ.md` và `faq_dataset.json`, 254 nhóm thuật ngữ, 50 kịch bản hội thoại và 20 intent. Tất cả nội dung khởi tạo đang ở trạng thái `draft`.

## Trạng thái và duyệt

Các tài liệu khởi tạo mang trạng thái `draft`. Chúng chứa hướng dẫn chung và mô tả mã nguồn, không phải quy chế của trường. Trước khi dùng với sinh viên thật: người phụ trách tuyển sinh/đào tạo/tài chính/công tác sinh viên rà soát đúng phạm vi; admin ghi nguồn, hiệu lực, năm học, người duyệt, ngày duyệt; chuyển trạng thái sang approved theo quy trình quản trị nội bộ.

## Nạp vào Study

Các file trong thư mục dự án chưa tự động được nạp vào database. Sau khi chuyên môn duyệt, admin cần tải từng Markdown lên Study qua **Quản lý FAQ / Kho tri thức AI**; khi trạng thái là `ready`, chatbot mới truy xuất được tài liệu đó. Study hỗ trợ upload `.md`, `.markdown`, `.txt`, `.docx`, `.pdf` (tối đa 10 MB mỗi tệp). Khi nạp Markdown, backend bỏ YAML front matter khỏi nội dung tìm kiếm nhưng giữ tiêu đề, chủ đề và phạm vi áp dụng làm ngữ cảnh. Khi chưa cấu hình provider LLM, chatbot chỉ tra cứu FAQ/tài liệu và hiển thị nguồn, chưa tổng hợp bằng LLM.

Nạp các file nhỏ trong nhóm đã duyệt. Không tải `faq_dataset.json`, `intent_catalog.json` hoặc tài liệu còn draft vào production nếu chưa có pipeline chuyển đổi và review. Markdown giữ heading thuận tiện cho chunking. File lớn/nhạy cảm cần kiểm tra access/retention trước upload.

## Cập nhật phiên bản

Không sửa âm thầm một chính sách đã duyệt. Tạo bản mới, tăng version, cập nhật `last_updated`, source link, effective dates và người review; archive bản hết hiệu lực. So sánh FAQ và intent để tránh câu trả lời mâu thuẫn. Sau cập nhật, xóa/re-ingest document cũ theo quy trình admin hiện có và chạy bộ eval.

## Các trường còn thiếu cần chủ sở hữu nghiệp vụ cung cấp

- Tên pháp lý, địa chỉ, hotline và domain của trường (Study chưa gắn với trường thật).
- Đề án tuyển sinh từng năm, ngành/chỉ tiêu/tổ hợp/điểm chuẩn và lịch đã duyệt.
- Chương trình đào tạo từng ngành/khóa, tín chỉ, rubric điểm, chuẩn đầu ra.
- Biểu phí theo khóa/học kỳ, quy trình đối soát, miễn giảm, học bổng và hoàn phí.
- Thủ tục, mẫu biểu, nơi nhận, thời gian/SLA và đầu mối phụ trách.
- Nội quy, chính sách sinh viên, kênh tư vấn sức khỏe/tâm lý, quy trình khẩn cấp.
- Quy trình nhân sự và phân quyền được ban hành.
- Ngày hiệu lực, nguồn chính thức, người phê duyệt và lịch review định kỳ cho từng nội dung.

## Quyền riêng tư và vận hành

Không đưa hồ sơ sinh viên/nhân viên, bảng điểm, mã định danh hoặc email thật vào KB dùng chung. Tách knowledge public và data riêng; API là nơi kiểm tra object-level permission. Admin chỉ nạp dữ liệu có quyền sử dụng. Với yêu cầu sửa/xóa hoặc thông tin pháp lý nhạy cảm, hỏi DPO/pháp chế/đầu mối hệ thống.
