# Ma trận coverage câu hỏi NEU AI

Tài liệu nội bộ. Mức coverage phản ánh nội dung hiện có trong Markdown, không phải kết quả kiểm thử model hay xác nhận tài liệu đã được nạp vào database.

| Nhóm intent | Coverage hiện tại | Tài liệu chính | Cách xử lý khi thiếu |
|---|---|---|---|
| Nhận diện, tên trường, lịch sử và sứ mệnh | Có nguồn | `00_core/*.md` | Dẫn website chính thức; không tự thêm mốc/xếp hạng |
| Địa chỉ, cơ sở, liên hệ | Có nguồn một phần | `00_core/campus_and_facilities.md`, `official_contacts.md` | Xác minh thông tin liên hệ hiện hành trên trang NEU |
| Tuyển sinh chính quy năm 2026 | Có nguồn theo văn bản năm | `01_admissions/yearly/2026/admission_plan.md` | Với năm khác, không suy diễn; tìm thông báo chính thức đúng năm |
| Điểm chuẩn 2026 | Có nguồn cho 10 chương trình dự án | `01_admissions/yearly/2026/admission_scores.md` | Nêu rõ đây không phải toàn bộ chương trình; không dự đoán điểm |
| 10 chương trình K68-2026 | Có nguồn chính thức cho tập con | `02_majors/majors_catalog.md` và 10 hồ sơ ngành | Tìm trên portal nếu hỏi chương trình ngoài danh mục |
| So sánh sáu cặp ngành | Có đối chiếu chương trình | `02_majors/major_comparison.md` | Không kết luận ngành nào “tốt hơn”; hỏi mục tiêu cá nhân nếu cần tư vấn |
| GPA, thi, tín chỉ, đăng ký, học lại, bảo lưu | Chỉ có đường dẫn tra cứu | `03_academic/academic_services_guide.md`, FAQ sinh viên | Dẫn Phòng Quản lý đào tạo/cổng sinh viên; cần khóa và quy định hiện hành |
| Học phí năm học 2026–2027 | Có nguồn theo quyết định được dẫn | `04_financial_aid/tuition_and_financial_aid_2026_2027.md` | Không ngoại suy sang năm sau hoặc tính số tiền cá nhân khi thiếu dữ liệu |
| Học bổng và miễn giảm | Có điều kiện/nhóm đối tượng một phần | Cùng tài liệu tài chính | Giá trị, hồ sơ và thời hạn cần thông báo của đợt cụ thể |
| Ký túc xá, thư viện, y tế và hỗ trợ | Có danh mục cổng/đầu mối | `05_student_life/student_services_directory.md` | Không bịa sức chứa, giờ mở cửa, tiêu chí hay thời hạn |
| Thủ tục hành chính | Có hướng dẫn nơi tra cứu | `05_student_life/administrative_procedures.md` | Dẫn OneGate/đơn vị phụ trách; không tự tạo quy trình chi tiết |
| Nghề nghiệp/thực tập | Có hướng dẫn chuẩn bị và cổng việc làm | `06_career/career_preparation.md` | Tình trạng tin tuyển dụng thay đổi; kiểm tra cổng việc làm trực tiếp |
| Cổng số của NEU | Có liên kết và hướng dẫn tổng quát | `07_digital_services/neu_student_portal_guide.md` | Kiểm tra link hiện hành, không yêu cầu người dùng chia sẻ mật khẩu |
| Chatbot/kho tri thức của dự án | Có hướng dẫn theo source UI | `07_digital_services/neu_ai_app_guide.md`, `08_faq/chatbot_faq.md` | Không nhầm ứng dụng repository với cổng chính thức NEU |
| Thông tin cá nhân/hồ sơ thực tế | Không có dữ liệu đủ căn cứ trong bộ tài liệu | Không có | Không tiết lộ/đoán; người dùng đăng nhập cổng được trường cấp hoặc liên hệ đơn vị |
| Tuyển sinh 2027 trở đi | Chưa có nguồn trong bộ hiện tại | Chưa có | Xin người dùng nêu năm; kiểm tra thông báo NEU đúng mùa |

## Bộ câu hỏi kiểm tra

`question_catalog.md` có 160 câu duy nhất, 16 câu cho từng nhóm: nhận diện; tuyển sinh/điểm; ngành; học vụ; tài chính; dịch vụ người học; nghề nghiệp; cổng số; chatbot; tình huống ranh giới/không đủ dữ liệu.

Mỗi lần cập nhật nội dung, chạy thủ công một mẫu câu từ các nhóm liên quan và ghi kết quả trong báo cáo mới. Không đánh dấu “đã qua” chỉ vì câu hỏi có tài liệu tương ứng.
