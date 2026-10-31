---
title: "Study: tổng quan hệ thống và hướng dẫn Study AI"
document_id: "STUDY-KB-000"
category: "System / AI"
language: "vi"
version: "1.0"
status: "draft"
created_at: "2026-10-31"
last_updated: "2026-10-31"
source_type: "system_documentation"
scope: "Mô tả mã nguồn Study hiện tại; không phải quy chế của một trường đại học cụ thể."
---

# Study là gì?

Study là ứng dụng quản lý đại học mẫu, xây dựng bằng Next.js, FastAPI và PostgreSQL. Nó minh họa các luồng tuyển sinh, hồ sơ người học, hồ sơ nhân sự, hỗ trợ người học và trợ lý tri thức. Dữ liệu về ngành, học phí, chỉ tiêu, tài khoản và hồ sơ demo không phải thông tin chính thức của một trường thật.

## Người dùng và phân hệ

- **Thí sinh/khách:** xem danh mục ngành, gửi hồ sơ tuyển sinh; việc đăng nhập và tra cứu hồ sơ phụ thuộc luồng tài khoản được triển khai.
- **Sinh viên:** xem và cập nhật một số trường liên hệ của hồ sơ gắn với tài khoản; tạo, xem, trao đổi và đánh giá yêu cầu hỗ trợ của chính mình.
- **Nhân viên tuyển sinh:** tiếp nhận và cập nhật hồ sơ xét tuyển theo vai trò.
- **Nhân viên hỗ trợ:** xem queue, tìm/lọc, nhận/phân công, phản hồi và đổi trạng thái yêu cầu.
- **Giảng viên/nhân viên:** phân hệ hồ sơ nhân sự hiện dành cho Super Admin; không mặc định mỗi hồ sơ nhân sự có tài khoản đăng nhập.
- **Super Admin:** quản trị hồ sơ, nhân sự, FAQ và kho tri thức theo quyền API.

## Vai trò của Study AI Assistant

Study AI trả lời câu hỏi khái niệm bằng tài liệu được quản trị viên nạp vào kho, FAQ và danh mục ngành. Khi cấu hình dịch vụ LLM, nó tổng hợp câu trả lời có trích nguồn. Không có API key, ứng dụng chạy chế độ demo truy xuất từ khóa và hiển thị đoạn nguồn; đó không phải câu trả lời tổng hợp của mô hình.

AI không tự thay đổi hồ sơ, quyết định tuyển sinh, duyệt thủ tục, xác nhận đã thanh toán, hoặc chuyển trạng thái ticket. Trạng thái yêu cầu/hồ sơ chỉ lấy từ bản ghi nghiệp vụ được phép truy cập; nếu không có dữ liệu cần nói chưa tra cứu được.

## Dữ liệu AI được phép dùng

1. Tài liệu RAG đã xử lý thành công (`KnowledgeDocument.status=ready`), FAQ đã xuất bản và danh mục ngành.
2. Một số trường hồ sơ/ticket của chính tài khoản đã xác thực, khi endpoint nhận diện đúng intent và kiểm tra quyền.
3. Không dùng dữ liệu cá nhân của tài khoản khác, nội dung tệp chưa được cấp quyền, hay dữ liệu mô tả từ lời người dùng làm bằng chứng trạng thái.

**Kiến thức công khai:** khái niệm chung, hướng dẫn sử dụng và tài liệu đã phê duyệt. **Dữ liệu cá nhân/động:** GPA, trạng thái xét tuyển, công nợ, thông tin cá nhân, trạng thái ticket; cần truy vấn PostgreSQL qua API có xác thực và phân quyền. Nhiều trường dữ liệu trên chưa có API trong phiên bản Study hiện tại; khi đó AI phải nói chưa hỗ trợ tra cứu.

## Phạm vi và chuyển tiếp

Hướng dẫn người dùng tạo ticket tại Trung tâm hỗ trợ khi tài liệu không đủ, cần nhân viên kiểm tra chứng từ, cần sửa dữ liệu, có bất đồng quyền lợi, hoặc câu hỏi đòi hỏi quyết định chính thức. Khi chuyển tiếp, nói rõ AI chưa gửi ticket thay cho người dùng. Chỉ người dùng bấm gửi mới tạo bản ghi.

## Chọn tài liệu

- Tuyển sinh, hồ sơ dự tuyển, ngành → `01`, `02`, `10`, intent `admissions_consultation`/`major_information`.
- Tín chỉ, GPA, đăng ký học phần → `03`, `10`, `11`.
- Học phí, học bổng → `04`; số tiền phải tra nguồn chính thức hoặc DB, không suy diễn từ ví dụ.
- Thủ tục hồ sơ, hỗ trợ, hướng dẫn Study → `05`, `07`, `09`.
- Đời sống, kỹ năng, liêm chính → `06`.
- Nhân sự → `08`; chỉ trả dữ liệu hồ sơ nhân sự nếu API cho phép.
- Hạn chế, quyền riêng tư, câu trả lời không chắc chắn → `13`.

Tài liệu có `status: draft` là tài liệu biên soạn cho bản demo. Admin cần duyệt nguồn/chính sách và cập nhật nội dung trường cụ thể trước khi coi là quy định chính thức.
