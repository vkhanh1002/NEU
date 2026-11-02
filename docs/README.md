# Tài liệu dự án NEU

Tài liệu này mô tả source hiện có, không phải đặc tả mong muốn. Nhãn `IMPLEMENTED`, `PARTIAL`, `NOT_IMPLEMENTED`, `UNVERIFIED`, `TESTED`, `NOT_TESTED` phân biệt trạng thái code với kiểm thử thực tế. Hệ thống là bản mô phỏng NEU; dữ liệu seed không phải dữ liệu nghiệp vụ chính thức của trường.

## Bắt đầu

- [Tổng quan](01_PROJECT_OVERVIEW.md) · [Yêu cầu/nghiệp vụ](02_BUSINESS_REQUIREMENTS.md) · [Kiến trúc](03_SYSTEM_ARCHITECTURE.md) · [Công nghệ](04_TECHNOLOGY_STACK.md)
- [Database](05_DATABASE_DESIGN.md) · [ERD](06_DATABASE_DIAGRAM.md) · [API](07_API_DOCUMENTATION.md) · [Auth](08_AUTHENTICATION_AUTHORIZATION.md) · [Phân quyền](09_ROLE_PERMISSION_MATRIX.md)
- [Frontend](10_FRONTEND_DOCUMENTATION.md) · [Backend](11_BACKEND_DOCUMENTATION.md) · [AI](12_AI_CHATBOT_ARCHITECTURE.md) · [RAG](13_RAG_KNOWLEDGE_BASE.md) · [Luồng nghiệp vụ](14_BUSINESS_WORKFLOWS.md)
- [Seed/test account](15_SEED_DATA_AND_TEST_ACCOUNTS.md) · [Docker](16_DOCKER_AND_DEPLOYMENT.md) · [Cài Windows](17_INSTALLATION_GUIDE.md) · [Kiểm thử](18_TESTING_GUIDE.md) · [Hạn chế](19_KNOWN_ISSUES_AND_LIMITATIONS.md) · [Roadmap](20_DEVELOPMENT_ROADMAP.md)
- Sơ đồ: [system](diagrams/system_architecture.mmd), [ERD](diagrams/database_erd.mmd), [workflows](14_BUSINESS_WORKFLOWS.md). Developer: [guides](guides/).

## Chạy nhanh (PowerShell)

Từ thư mục repository: `Copy-Item .env.example .env` (chỉ lần đầu), điền secret/provider cần thiết, `docker compose up --build -d`, kiểm tra `docker compose ps`. Không dùng `down -v` nếu cần giữ database.

## Phạm vi xác minh

Tài liệu được tổng hợp từ source trong repository tại ngày 2026-11-03. Version runtime lấy từ manifest/requirements. Chưa xác nhận trạng thái Docker đang chạy hay thông tin NEU từ dữ liệu seed. API chi tiết chuẩn tham chiếu OpenAPI tại `/docs` khi backend chạy.
