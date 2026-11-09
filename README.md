# NEU University Management System

Nền tảng nội bộ mô phỏng cổng thông tin và nghiệp vụ đại học, gồm Next.js, FastAPI, PostgreSQL/pgvector và trợ lý AI tra cứu tri thức. Tên trường, quy trình và dữ liệu seed cần được rà soát trước khi dùng như thông tin chính thức.

## Chạy bằng Docker Desktop trên Windows

Mở Docker Desktop, mở PowerShell tại thư mục gốc dự án rồi chạy:

```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
docker compose up --build -d
docker compose ps
docker compose logs --tail=100 backend
```

Khi `db` và `backend` báo `healthy`, mở http://localhost:3000. API: http://localhost:8000; OpenAPI: http://localhost:8000/docs. Compose tự chạy Alembic đến revision mới nhất rồi chạy seed; các lần seed lặp lại không tạo trùng các mã ổn định. Nếu sửa `.env`, chạy lại `docker compose up --build -d` để recreate container. Dùng `docker compose down` để dừng. Tránh `docker compose down -v` vì sẽ xóa dữ liệu database.

## Cấu hình production trên Render

- Frontend (Docker): đặt `NEXT_PUBLIC_API_URL` thành URL công khai của Backend, có cả tiền tố `/api/v1` (ví dụ `https://<backend>.onrender.com/api/v1`) rồi rebuild/deploy frontend. Next.js đóng gói biến `NEXT_PUBLIC_*` vào bundle lúc build; đổi biến khi runtime không đổi URL đã đóng gói.
- Backend: đặt `CORS_ORIGINS` thành origin frontend chính xác (ví dụ `https://<frontend>.onrender.com`, không thêm đường dẫn `/api/v1`). Nếu có nhiều origin, phân cách bằng dấu phẩy.
- Backend cũng cần `DATABASE_URL` trỏ tới PostgreSQL bền vững và `SECRET_KEY` riêng của môi trường production. Không dùng `localhost` làm API URL hoặc database host trên Render; không commit giá trị bí mật.

Docker Compose local đặt sẵn `NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1` và `CORS_ORIGINS=http://localhost:3000`. Có thể ghi đè hai biến này trong `.env`.

## Tài khoản kiểm thử cục bộ

Seed mới tạo các tài khoản dưới đây nếu chưa tồn tại. Bốn tài khoản cũ `@study.edu.vn` sẽ được chuyển sang địa chỉ NEU tương ứng; mật khẩu tự đặt được giữ nguyên. Tài khoản cũ còn dùng mật khẩu mặc định sẽ được đổi sang mật khẩu NEU bên dưới.

| Vai trò | Email | Mật khẩu seed mới |
| --- | --- | --- |
| Quản trị viên | `admin@neu.local` | `NEUStaff2026!` |
| Cán bộ tuyển sinh | `admissions@neu.local` | `NEUStaff2026!` |
| Cán bộ hỗ trợ | `support@neu.local` | `NEUStaff2026!` |
| Cán bộ nhân sự | `hr@neu.local` | `NEUStaff2026!` |
| Cán bộ đào tạo | `academic@neu.local` | `NEUStaff2026!` |
| Giảng viên | `lecturer@neu.local` | `NEUStaff2026!` |
| Sinh viên chính | `student@neu.local` | `NEUStudent2026!` |
| Sinh viên bổ sung | `student02@neu.local`–`student20@neu.local` | `NEUStudent2026!` |
| Thí sinh | `candidate01@example.test`–`candidate05@example.test` | `NEUApplicant2026!` |

Đây là tài khoản/mật khẩu phát triển, không dùng trên hệ thống công khai. Seed không ghi đè mật khẩu người dùng đã thay đổi.

## Dữ liệu seed

- 10 ngành và các khoa liên quan.
- 20 hồ sơ sinh viên được liên kết tài khoản; mỗi hồ sơ có dữ liệu hai học kỳ, học phần, điểm, lịch học/thi, rèn luyện, tài chính, bài tập và thông báo. Có 15 hồ sơ giảng viên/nhân viên và yêu cầu hỗ trợ nhiều trạng thái.
- 25 hồ sơ thí sinh gồm hồ sơ tiếp nhận, cần bổ sung, đang xét duyệt, đã duyệt, trúng tuyển, không đủ điều kiện và không trúng tuyển. Năm tài khoản thí sinh đầu tiên có thể đăng nhập để xem hồ sơ của mình.
- 11 bài viết thuộc nhiều danh mục. Năm sự kiện được giữ ở trạng thái chờ xác nhận nên không xuất hiện trên lịch công khai trước khi có lịch và địa điểm đã được duyệt.
- Các khoản thu và giao dịch là dữ liệu nội bộ phục vụ kiểm tra luồng hiển thị; không có cổng thanh toán thật.

Seed là bổ sung an toàn: không xóa volume và không thay thế các hồ sơ hiện có. Nếu database cũ chứa nhiều sinh viên hơn, seed giữ nguyên các hồ sơ đó và liên kết dữ liệu học tập cho tối đa 20 sinh viên đầu tiên.

## AI và Knowledge Base

Các khóa provider nằm trong `.env` ở thư mục gốc và chỉ được truyền vào backend. Không commit hoặc dán khóa vào giao diện/chat. AI sử dụng Groq làm primary và Gemini làm fallback theo cấu hình `.env.example`; model và hạn mức phụ thuộc cấu hình tài khoản. Chạy lại Compose sau khi đổi biến môi trường. Nếu cả hai provider thất bại, ứng dụng trả thông báo lỗi thay vì tạo câu trả lời giả.

Quản trị viên mở **Quản trị → Kho tri thức** để nạp tài liệu. Tài liệu mới chỉ dùng nội bộ; bật biểu tượng công khai cho tài liệu đã được duyệt trước khi Guest AI có thể truy xuất. Guest Chat lưu lịch sử theo token phiên ngẫu nhiên ở backend, token được giữ trong localStorage, và mỗi phiên chỉ đọc được lịch sử của chính nó. Guest RAG chỉ đọc FAQ đã xuất bản, danh mục ngành công khai và tài liệu được bật công khai. Không tải hồ sơ cá nhân hoặc tài liệu mật lên dịch vụ AI bên ngoài.

## Kiểm thử

Frontend, tại `frontend/`:

```powershell
npm test
npm run typecheck
npm run build
```

Backend, tại `backend/`:

```powershell
python -m pip install -r requirements.txt
python -m pytest tests
```

Các kiểm thử API dùng SQLite và không cần database production. Có thể kiểm tra endpoint qua `/docs` khi backend khỏe.

## Thành phần chính

- Guest: đúng ba mục **Giới thiệu**, **Tuyển sinh**, **Tin tức và sự kiện**; chatbot tuyển sinh dùng API tra cứu công khai có giới hạn tần suất và lịch sử phiên riêng.
- Student: tiến độ, hồ sơ cá nhân, lịch học, lịch thi, kết quả/GPA, rèn luyện, tài chính, bài tập, thông báo và yêu cầu hỗ trợ.
- Lecturer: dashboard theo dữ liệu phân công, thời khóa biểu, lớp học phần, danh sách sinh viên, nhập điểm các trường hiện có với lịch sử trước/sau, phiên điểm danh và duyệt yêu cầu điểm danh bù.
- Smart Attendance: phiên và lượt điểm danh dùng chung giữa giảng viên/sinh viên; ảnh chụp trực tiếp được nhận trong lúc phiên mở, yêu cầu chỉ gửi sau khi kết thúc, duyệt Muộn/Vắng có audit log. Ảnh lưu ở Docker volume riêng `neu_attendance_uploads`, tách biệt volume PostgreSQL.
- Thương hiệu: logo, ảnh nền sảnh và favicon lấy từ ảnh người dùng cung cấp trong `frontend/public/brand/`.
- Student và giảng viên đọc cùng bản ghi lớp học phần; cấu hình ca học tập trung tại `backend/app/services/schedule.py`. Giờ ca hiện là khung tham khảo, không thay thế lịch chính thức đã được trường xác nhận.
- Staff: nghiệp vụ theo vai trò; kiểm tra quyền ở backend.
- Database: migration `0001`–`0014`; nâng cấp applicant details, news provenance, Smart Attendance và audit điểm theo migration bổ sung, không xóa dữ liệu hiện có.

Xem [hướng dẫn demo Smart Attendance](docs/smart-attendance-demo.md) để chạy luồng camera và duyệt yêu cầu bằng các tài khoản mẫu.
