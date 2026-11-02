"""Idempotently import answerable Markdown from the repository KB through the normal RAG processor."""
import argparse
import asyncio
import hashlib
import re
from pathlib import Path

from sqlalchemy import func, select

from app.ai.rag import extract_document, ingest_document
from app.core.database import SessionLocal
from app.models import KnowledgeChunk, KnowledgeDocument, User

PROJECT_ROOT = Path(__file__).resolve().parents[3]
KB_ROOT = next((candidate for candidate in (Path("/app/knowledge_base"), PROJECT_ROOT / "knowledge_base")
                if candidate.exists()), PROJECT_ROOT / "knowledge_base")
SKIP_PARTS = {"ai_metadata", "archive", "backup", "backups", "_archive", "_backup"}


def discover_files(root: Path = KB_ROOT) -> list[Path]:
    return sorted(path for path in root.rglob("*.md")
                  if not any(part.lower() in SKIP_PARTS for part in path.relative_to(root).parts[:-1])
                  and path.name.lower() not in {"readme.md", "knowledge_index.md"}
                  and not path.name.lower().endswith((".bak.md", ".backup.md")))


def metadata_value(text: str, key: str) -> str | None:
    match = re.search(rf"(?m)^{re.escape(key)}:\s*(.+?)\s*$", text)
    return match.group(1).strip().strip("\"'") if match else None


async def run(apply: bool, prune: bool) -> int:
    files = discover_files()
    report = {"discovered": len(files), "valid": 0, "unchanged": 0, "imported": 0,
              "updated": 0, "skipped": 0, "duplicate_content": 0, "metadata_missing": 0,
              "failed": 0, "chunks": 0, "errors": []}
    parsed = []
    for path in files:
        try:
            raw = path.read_bytes()
            text = extract_document(path.name, raw)
            if not text.strip():
                raise ValueError("Không có văn bản sau khi trích xuất")
            decoded = raw.decode("utf-8-sig", errors="strict")
            if not decoded.startswith("---\n") and not decoded.startswith("---\r\n"):
                report["metadata_missing"] += 1
            relative = path.relative_to(KB_ROOT).as_posix()
            status = metadata_value(decoded, "source_status") or "unverified"
            year_text = metadata_value(decoded, "year")
            if status not in {"verified", "partially_verified", "unverified", "demo"}:
                raise ValueError(f"source_status không hợp lệ: {status}")
            year = int(year_text) if year_text and year_text.isdigit() else None
            parsed.append((path, relative, raw, hashlib.sha256(raw).hexdigest(), status, year))
            report["valid"] += 1
        except Exception as exc:
            report["failed"] += 1
            report["errors"].append({"file": str(path.relative_to(KB_ROOT)), "error": str(exc)})

    db = SessionLocal()
    try:
        admin = db.scalar(select(User).where(User.role == "super_admin").order_by(User.created_at)) if apply else None
        if apply and not admin:
            raise RuntimeError("Không tìm thấy tài khoản super_admin để gắn người nạp tài liệu.")
        current = {doc.source_path: doc for doc in db.scalars(select(KnowledgeDocument).where(
            KnowledgeDocument.source_path.is_not(None))).all()}
        discovered_paths = {item[1] for item in parsed}
        seen_hashes: set[str] = set()
        for path, relative, raw, digest, status, year in parsed:
            if digest in seen_hashes:
                report["duplicate_content"] += 1
                continue
            seen_hashes.add(digest)
            prior = current.get(relative)
            if prior and prior.content_hash == digest and prior.status == "ready":
                report["unchanged"] += 1
                continue
            if not apply:
                report["updated" if prior else "imported"] += 1
                continue
            if prior:
                old_chunks = db.scalars(select(KnowledgeChunk).where(KnowledgeChunk.document_id == prior.id)).all()
                for chunk in old_chunks:
                    db.delete(chunk)
                prior.filename = relative
                prior.media_type = "text/markdown"
                prior.status = "processing"
                prior.error = None
                prior.content_hash = digest
                prior.source_status = status
                prior.source_year = year
                prior.is_public = False
                document = prior
                report["updated"] += 1
            else:
                document = KnowledgeDocument(filename=relative, media_type="text/markdown", uploaded_by=admin.id,
                                             source_path=relative, content_hash=digest,
                                             source_status=status, source_year=year, is_public=False)
                db.add(document)
                db.flush()
                report["imported"] += 1
            await ingest_document(db, document, raw)
            if document.status == "failed":
                report["failed"] += 1
                report["errors"].append({"file": relative, "error": document.error or "Ingestion thất bại"})
            else:
                report["chunks"] += len(db.scalars(select(KnowledgeChunk).where(KnowledgeChunk.document_id == document.id)).all())
        report["embeddings_stored"] = db.scalar(select(func.count()).select_from(KnowledgeChunk).where(KnowledgeChunk.embedding.is_not(None))) or 0
        if prune:
            stale = [doc for name, doc in current.items() if name not in discovered_paths]
            if apply:
                for doc in stale:
                    db.delete(doc)
                db.commit()
            report["pruned"] = len(stale)
        report["skipped"] = report["discovered"] - report["valid"]
        print(report)
        return 1 if report["failed"] else 0
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Persist changes. Without this flag, only preview.")
    parser.add_argument("--prune", action="store_true", help="Remove imported KB records whose source files were deleted.")
    args = parser.parse_args()
    raise SystemExit(asyncio.run(run(args.apply, args.prune)))


if __name__ == "__main__":
    main()
