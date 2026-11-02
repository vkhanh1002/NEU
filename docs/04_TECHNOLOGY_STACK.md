# Công nghệ

| Thành phần | Công nghệ/version xác minh | Vai trò |
|---|---|---|
| Frontend | Next.js 16.4.3, React 19.3.1, TypeScript 5.8.3 | App Router, UI |
| Backend | Python; FastAPI 0.162.0, Uvicorn 0.34.2 | REST API |
| ORM/schema | SQLAlchemy 2.0.40 | PostgreSQL access |
| Migration | Alembic 1.15.2 | Schema migrations |
| Database | `pgvector/pgvector:pg16`; PostgreSQL 16 image | Relational + vector |
| Vector type | pgvector 0.4.0; dimension 1536 | Knowledge embeddings |
| Auth | PyJWT 2.10.1, pwdlib[argon2] 0.2.1 | JWT/password hash |
| AI | HTTP provider adapters in `app/ai/providers.py` | Groq/Gemini configurable |
| Containers | Docker Compose | Local multi-service |

Versions are from `frontend/package.json`, `backend/requirements.txt`, `docker-compose.yml`; Python runtime exact base image version must be read from Dockerfile. Current config defaults: Groq primary, model `openai/gpt-oss-20b`; Gemini fallback `gemini-3.8-flash`. Embedding model/provider activation depends on runtime config; do not infer from vector dimension. See [RAG](13_RAG_KNOWLEDGE_BASE.md).
