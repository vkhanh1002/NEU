# Kiến trúc

Frontend Next.js App Router (port 3000) gọi REST `/api/v1` ở FastAPI (8000). Backend dùng SQLAlchemy/Alembic với PostgreSQL 16 + pgvector. LLM provider được gọi từ backend qua HTTP; browser không giữ provider key. Compose chạy db, backend, frontend. Sơ đồ: [system_architecture.mmd](diagrams/system_architecture.mmd).

## Luồng

Browser → Next UI/API client → FastAPI router → dependency xác thực/role → SQLAlchemy service/query → PostgreSQL. Với chat: backend tải history, truy xuất FAQ/catalog/knowledge (lọc public với guest), dựng context, gọi provider và lưu message + sources. Guest token hash được lưu DB; raw token giữ phía client.

## Khởi động / migrations

FastAPI app tại `backend/app/main.py`; startup chạy Alembic migrations. Dockerfile build riêng mỗi service. Health endpoint `/health`. Không thấy deployment orchestration ngoài Compose; production topology chưa xác minh.
