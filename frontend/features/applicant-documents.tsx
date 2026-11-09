"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { Check, Download, FilePlus2, LoaderCircle, Trash2, Upload } from "lucide-react";
import { api, authenticatedFetch } from "@/lib/api";
import { ErrorNotice } from "@/components/ui";

export const APPLICANT_DOCUMENT_TYPES = [
  { id: "cccd_front", label: "CCCD/CMND mặt trước" },
  { id: "cccd_back", label: "CCCD/CMND mặt sau" },
  { id: "portrait", label: "Ảnh chân dung" },
  { id: "transcript", label: "Học bạ / bảng điểm" },
  { id: "graduation_proof", label: "Giấy chứng nhận tốt nghiệp" },
  { id: "exam_result", label: "Phiếu điểm thi" },
  { id: "language_certificate", label: "Chứng chỉ ngoại ngữ" },
  { id: "international_certificate", label: "Chứng chỉ quốc tế" },
  { id: "academic_achievement", label: "Minh chứng thành tích học tập" },
  { id: "priority_proof", label: "Minh chứng ưu tiên" },
  { id: "other", label: "Tài liệu khác" },
] as const;

export type ApplicantDocument = {
  id: string;
  document_type: string;
  filename: string;
  media_type: string;
  size_bytes: number;
  status: string;
  review_note: string;
  uploaded_at: string;
  reviewed_at: string | null;
};

const REVIEW_STATES = ["Chờ kiểm tra", "Đã xác nhận", "Cần bổ sung"];
const MAX_FILE_BYTES = 10 * 1024 * 1024;
const ACCEPTED_EXTENSIONS = [".pdf", ".docx", ".png", ".jpg", ".jpeg"];

function documentLabel(id: string) {
  return APPLICANT_DOCUMENT_TYPES.find(item => item.id === id)?.label ?? id;
}

export function ApplicantDocumentManager({ applicantId, isStaff }: { applicantId: string; isStaff: boolean }) {
  const [documents, setDocuments] = useState<ApplicantDocument[]>([]);
  const [documentType, setDocumentType] = useState<string>(APPLICANT_DOCUMENT_TYPES[0].id);
  const [file, setFile] = useState<File | null>(null);
  const [statuses, setStatuses] = useState<Record<string, string>>({});
  const [notes, setNotes] = useState<Record<string, string>>({});
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [opened, setOpened] = useState(false);
  const uploadInput = useRef<HTMLInputElement>(null);

  const load = useCallback(async () => {
    try {
      const rows = await api<ApplicantDocument[]>(`/admissions/applications/${applicantId}/documents`);
      setDocuments(rows);
      setStatuses(current => Object.fromEntries(rows.map(row => [row.id, current[row.id] ?? row.status])));
      setNotes(current => Object.fromEntries(rows.map(row => [row.id, current[row.id] ?? row.review_note])));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Không thể tải danh sách tài liệu.");
    }
  }, [applicantId]);

  useEffect(() => { if (opened) void load(); }, [opened, load]);

  async function upload() {
    if (!file) { setError("Chọn một tệp trước khi tải lên."); return; }
    const extension = `.${file.name.split(".").pop()?.toLowerCase() ?? ""}`;
    if (!ACCEPTED_EXTENSIONS.includes(extension)) { setError("Chỉ nhận PDF, DOCX, PNG hoặc JPG/JPEG."); return; }
    if (file.size > MAX_FILE_BYTES) { setError("Mỗi tài liệu có dung lượng tối đa 10 MB."); return; }
    const body = new FormData();
    body.set("document_type", documentType);
    body.set("file", file);
    setBusy("upload"); setError(""); setMessage("");
    try {
      await api(`/admissions/applications/${applicantId}/documents`, { method: "POST", body });
      setFile(null); if (uploadInput.current) uploadInput.current.value = "";
      setMessage("Đã tải tài liệu lên. Tài liệu đang chờ kiểm tra.");
      await load();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Tải tài liệu chưa thành công.");
    } finally { setBusy(""); }
  }

  async function download(row: ApplicantDocument) {
    setBusy(row.id); setError("");
    try {
      const response = await authenticatedFetch(`/admissions/applications/${applicantId}/documents/${row.id}/download`);
      if (!response.ok) throw new Error("Không thể tải tài liệu này.");
      const url = URL.createObjectURL(await response.blob());
      const anchor = document.createElement("a");
      anchor.href = url; anchor.download = row.filename; anchor.click();
      window.setTimeout(() => URL.revokeObjectURL(url), 1000);
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Tải tài liệu chưa thành công."); }
    finally { setBusy(""); }
  }

  async function remove(row: ApplicantDocument) {
    setBusy(row.id); setError(""); setMessage("");
    try {
      await api(`/admissions/applications/${applicantId}/documents/${row.id}`, { method: "DELETE" });
      setMessage("Đã xóa tài liệu."); await load();
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Không thể xóa tài liệu."); }
    finally { setBusy(""); }
  }

  async function review(row: ApplicantDocument) {
    setBusy(row.id); setError(""); setMessage("");
    try {
      await api(`/admissions/applications/${applicantId}/documents/${row.id}/review`, {
        method: "PATCH", body: JSON.stringify({ status: statuses[row.id] ?? row.status, note: notes[row.id] ?? "" }),
      });
      setMessage("Đã cập nhật kết quả kiểm tra và gửi thông báo cho thí sinh."); await load();
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Không thể cập nhật tài liệu."); }
    finally { setBusy(""); }
  }

  return <details className="applicant-documents" onToggle={event => setOpened(event.currentTarget.open)}>
    <summary><FilePlus2 size={17} /> Tài liệu hồ sơ <span>{documents.length}</span></summary>
    {error && <ErrorNotice message={error} />}
    {message && <div className="document-success"><Check size={15} />{message}</div>}
    {documents.length > 0 && <div className="document-list">{documents.map(row => <article className="document-row" key={row.id}>
      <div className="document-row-info"><strong>{documentLabel(row.document_type)}</strong><span>{row.filename} · {(row.size_bytes / 1024 / 1024).toFixed(2)} MB</span><small>{new Date(row.uploaded_at).toLocaleDateString("vi-VN")} · {row.status}</small>{row.review_note && <small className="document-review-note">{row.review_note}</small>}</div>
      <div className="document-row-actions"><button className="mini-button" disabled={!!busy} onClick={() => void download(row)} aria-label={`Tải ${row.filename}`}><Download size={15} /> Tải xuống</button>
        {!isStaff && row.status !== "Đã xác nhận" && <button className="mini-button danger-mini" disabled={!!busy} onClick={() => void remove(row)} aria-label={`Xóa ${row.filename}`}><Trash2 size={15} /> Xóa</button>}
      </div>
      {isStaff && <div className="document-review-controls"><select aria-label={`Trạng thái ${row.filename}`} value={statuses[row.id] ?? row.status} onChange={event => setStatuses(current => ({ ...current, [row.id]: event.target.value }))}>{REVIEW_STATES.map(status => <option key={status}>{status}</option>)}</select><input maxLength={1000} value={notes[row.id] ?? ""} onChange={event => setNotes(current => ({ ...current, [row.id]: event.target.value }))} placeholder="Ghi chú / nội dung cần bổ sung" /><button className="mini-button" disabled={!!busy} onClick={() => void review(row)}>{busy === row.id ? <LoaderCircle size={15} className="spin" /> : <Check size={15} />} Lưu</button></div>}
    </article>)}</div>}
    {!isStaff && <div className="document-upload-controls"><label>Loại tài liệu<select value={documentType} onChange={event => setDocumentType(event.target.value)}>{APPLICANT_DOCUMENT_TYPES.map(item => <option key={item.id} value={item.id}>{item.label}</option>)}</select></label><label>Tệp tải lên<input ref={uploadInput} type="file" accept=".pdf,.docx,.png,.jpg,.jpeg" onChange={event => setFile(event.target.files?.[0] ?? null)} /><small>{file ? `${file.name} · ${(file.size / 1024 / 1024).toFixed(2)} MB` : "PDF, DOCX, PNG hoặc JPG/JPEG · tối đa 10 MB"}</small></label><button className="button button-secondary" disabled={!!busy || !file} onClick={() => void upload()}>{busy === "upload" ? <LoaderCircle size={16} className="spin" /> : <Upload size={16} />} Tải tài liệu</button></div>}
    {!documents.length && <p className="document-empty">Chưa có tài liệu được tải lên.</p>}
  </details>;
}

export function SelectedFilePreview({ file }: { file: File }) {
  const [previewUrl, setPreviewUrl] = useState("");
  useEffect(() => {
    if (!file.type.startsWith("image/")) { setPreviewUrl(""); return; }
    const url = URL.createObjectURL(file); setPreviewUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);
  return <span className="selected-file-preview">{previewUrl && <img src={previewUrl} alt={`Xem trước ${file.name}`} />}<span>{file.name} · {(file.size / 1024 / 1024).toFixed(2)} MB</span></span>;
}
