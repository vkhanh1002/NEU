# Khuyến nghị RAG cho tiếng Việt

## Ingestion

- Study upload accepts Markdown (`.md`/`.markdown`) alongside TXT, DOCX, and PDF. For Markdown, the current parser removes YAML front matter from searchable text and retains title, category, and scope as a short context prefix. Keep `document_id`, version, status, source link, and effective year in the governed source file.
- Dùng Markdown UTF-8, giữ heading/category/version/status/scope/source link/effective year trong nguồn được quản trị; không nhúng YAML thô vào embedding.
- Chỉ index tài liệu được duyệt (`approved`); corpus hiện có `draft`, do đó admin cần duyệt trước production. Tách policy không rõ nguồn khỏi tài liệu answerable.
- Không trộn dữ liệu động (GPA, ticket, kết quả, học phí hiện hành) vào file tĩnh. Truy vấn PostgreSQL qua tool/API riêng có authorization.
- Với PDF scan cần OCR và báo nguồn OCR; nếu không trích được chữ, không đánh dấu ready.

## Chunking đề xuất

Tiếng Việt chứa khoảng trắng trong từ ghép, vì vậy không tách theo từ đơn. Bắt đầu bằng chunk theo heading/tiểu mục, sau đó chia mềm ở ranh giới câu/đoạn:

- 700–1.000 ký tự Unicode hoặc xấp xỉ 350–550 tokens tùy tokenizer.
- Overlap 100–160 ký tự (khoảng 15–20%) trong cùng mục; không kéo nội dung sang chủ đề khác.
- Giữ tiêu đề tài liệu + breadcrumb heading + metadata trong mỗi chunk; không nhúng YAML thô vào embedding.
- FAQ mỗi câu trả lời 1 chunk riêng; scenario làm ví dụ dialog, đánh dấu `example_only=true` để không bị nhầm thành policy.
- Tránh chia giữa số liệu/điều kiện và ngoại lệ. Mỗi chunk nguồn pháp lý phải kèm văn bản, điều/khoản, effective date và scope.

## Retrieval/ranking

Kết hợp lexical BM25/keyword với dense embeddings đa ngôn ngữ; nếu có reranker, ưu tiên exact code/name và filter metadata trước reranking. Truy xuất top 8–12 ứng viên, rerank rồi đưa 3–5 nguồn tốt vào prompt. Query rewrite dùng lịch sử hội thoại nhưng luôn giữ từ phủ định, năm, tên trường và mã ticket. Có thể mở rộng từ đồng nghĩa trong `11_UNIVERSITY_GLOSSARY.md`; không nhập nhằng cặp khái niệm khác bản chất.

### Điểm số gợi ý

Kết hợp lexical 0.35 + dense 0.45 + reranker 0.20, sau đó hiệu chỉnh bằng tập eval thực tế. Không coi các trọng số là mặc định phổ quát. Dùng ngưỡng thấp nhất theo từng intent; intent luật/chính sách phải có citation official-source và date. Khi dưới ngưỡng, hỏi lại hoặc từ chối suy đoán.

## Metadata / lọc

`doc_id`, `category`, `intent`, `language`, `status`, `source_type`, `scope`, `school_id`, `program`, `cohort`, `effective_from`, `effective_to`, `verified_at`, `privacy_level`, `version`. Lọc role/tenant trước retrieval. Draft/expired chỉ dùng nội bộ hoặc bị loại khỏi trả lời.

## Dynamic data routing

| Câu hỏi | Nguồn chính | Guard |
|---|---|---|
| GPA là gì? | KB 03 | General explanation |
| GPA của em? | Academic API/DB | Login, own student record; API hiện chưa có |
| Ngành CNTT học gì? | KB 02 + majors catalog | Gắn nhãn chương trình demo |
| Em trúng tuyển chưa? | Admissions DB/API | Own record only; hiện student status lookup chưa exposed |
| Hồ sơ xét tuyển đang đâu? | Admissions DB/API | Auth/owner scope; nếu API thiếu, nói không tra được |
| Học phí ngành này hiện bao nhiêu? | Approved fee schedule/DB | Year/program and effective version; demo amount is not official |
| Cách gửi ticket? | KB 07 | Explain UI |
| Ticket của em đang đâu? | Support API | Auth, owner filter; don't infer from chat context |
| Xin tạo ticket | Explicit UI action/API | Show form; only claim created after success response |

## Đánh giá

Tạo bộ 100+ câu hỏi thật có paraphrase, lỗi chính tả, follow-up và câu mơ hồ; đo recall@k, citation precision, factuality, abstention, privacy leakage, dynamic routing. Kiểm tra mọi số liệu chính sách với reviewer. Có regression set cho prompt injection ẩn trong file, quyền khác role, dữ liệu trùng tên và ticket không thuộc user. Ghi answer + source IDs, không log secret/PII thừa.

Code Study hiện dùng chunk ký tự `size=900`, `overlap=140`, lexical scoring và vector pgvector nếu có key; đây là baseline. Parser hiện chưa giữ heading breadcrumb trên từng chunk và chunker làm phẳng khoảng trắng; heading-aware chunking nêu trên là khuyến nghị nâng cấp, chưa phải hành vi hiện tại. Nên thử nghiệm trên eval set thay vì đổi tham số mù quáng.
