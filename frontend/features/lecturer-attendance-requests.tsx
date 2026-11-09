"use client";

import { useCallback, useEffect, useState } from "react";
import { api, authenticatedFetch, ApiError, apiErrorMessage } from "@/lib/api";
import { ErrorNotice, PageTitle, StatusBadge } from "@/components/ui";

type ClassItem = { id: string; course_id?: string; course_code: string; course_name: string; section: string };
type RequestRow = { id: string; status: string; reason: string; request_reason: string; student_number: string; full_name: string; class_name: string; course_code: string; course_name: string; section: string; starts_at: string; received_at: string | null; photo_captured_at: string | null; submitted_at: string; minutes_late: number | null; evidence_id: string | null; has_request_photo: boolean };

export function LecturerAttendanceRequestsPage() {
  const [classes, setClasses] = useState<ClassItem[]>([]); const [items, setItems] = useState<RequestRow[]>([]);
  const [pendingCount, setPendingCount] = useState(0); const [offeringId, setOfferingId] = useState(""); const [courseId, setCourseId] = useState("");
  const [status, setStatus] = useState("all"); const [error, setError] = useState("");
  const [rejection, setRejection] = useState<Record<string, string>>({}); const [preview, setPreview] = useState("");
  const load = useCallback(async () => {
    const params = new URLSearchParams({ status }); if (offeringId) params.set("offering_id", offeringId); if (courseId) params.set("course_id", courseId);
    const data = await api<{ items: RequestRow[]; pending_count: number }>(`/lecturer/attendance/requests?${params}`);
    setItems(data.items); setPendingCount(data.pending_count);
  }, [offeringId, courseId, status]);
  useEffect(() => { void api<{ items: ClassItem[] }>("/lecturer/classes").then(data => setClasses(data.items)).catch(cause => setError(cause.message)); }, []);
  useEffect(() => { let live = true; const refresh = () => load().catch(cause => { if (live) setError(cause.message); }); void refresh(); const timer = window.setInterval(() => void refresh(), 20000); return () => { live = false; window.clearInterval(timer); }; }, [load]);
  async function decide(item: RequestRow, decision: "accepted" | "rejected") {
    const reason = rejection[item.id]?.trim() ?? "";
    if (decision === "rejected" && reason.length < 5) { setError("Nhập lý do từ chối (ít nhất 5 ký tự)."); return; }
    try { await api(`/lecturer/attendance/requests/${item.id}`, { method: "PATCH", body: JSON.stringify({ decision, reason }) }); setError(""); await load(); }
    catch (cause) { setError(cause instanceof Error ? cause.message : "Không xử lý được yêu cầu."); }
  }
  async function showEvidence(requestId: string) {
    try { const response = await authenticatedFetch(`/attendance/makeup-requests/${requestId}/photo`); if (!response.ok) throw new ApiError(apiErrorMessage(await response.json().catch(() => ({}))), response.status); setPreview(URL.createObjectURL(await response.blob())); }
    catch (cause) { setError(cause instanceof Error ? cause.message : "Không tải được ảnh minh chứng."); }
  }
  useEffect(() => () => { if (preview) URL.revokeObjectURL(preview); }, [preview]);
  function closePreview() { setPreview(""); }
  return <div className="attendance-page"><PageTitle eyebrow="GIẢNG DẠY" title="Yêu cầu điểm danh bù" description="Yêu cầu chỉ hiển thị cho giảng viên phụ trách lớp tương ứng." action={<span className="pending-count-summary">Đang chờ <strong>{pendingCount}</strong></span>} />{error && <ErrorNotice message={error} />}
    <div className="attendance-request-filters"><label>Môn học<select value={courseId} onChange={event => { setCourseId(event.target.value); setOfferingId(""); }}><option value="">Tất cả môn</option>{Array.from(new Map(classes.map(row => [row.course_id ?? row.course_code, row])).values()).map(row => <option value={row.course_id ?? row.course_code} key={row.course_id ?? row.course_code}>{row.course_code} — {row.course_name}</option>)}</select></label><label>Lớp học phần<select value={offeringId} onChange={event => setOfferingId(event.target.value)}><option value="">Tất cả lớp</option>{classes.filter(row => !courseId || (row.course_id ?? row.course_code) === courseId).map(row => <option value={row.id} key={row.id}>{row.course_code} · {row.section} — {row.course_name}</option>)}</select></label><label>Trạng thái<select value={status} onChange={event => setStatus(event.target.value)}><option value="all">Tất cả</option><option value="pending">Chờ xử lý</option><option value="accepted">Đã chấp nhận</option><option value="rejected">Đã từ chối</option></select></label></div>
    <div className="attendance-request-list">{items.map(item => <article className="attendance-request-card" key={item.id}><div><small>{item.course_code} · {item.section}</small><h2>{item.full_name} <span>{item.student_number}</span></h2><p>{item.course_name} · Lớp hành chính {item.class_name || "—"}</p><dl><div><dt>Buổi học</dt><dd>{new Date(item.starts_at).toLocaleString("vi-VN")}</dd></div><div><dt>Thời điểm chụp</dt><dd>{item.photo_captured_at ? new Date(item.photo_captured_at).toLocaleString("vi-VN") : "Không có thời gian ảnh"}</dd></div><div><dt>Gửi yêu cầu</dt><dd>{new Date(item.submitted_at).toLocaleString("vi-VN")}</dd></div></dl><section className="request-reason"><strong>Lý do sinh viên</strong><p>{item.request_reason}</p></section><div className="attendance-request-actions"><StatusBadge>{requestLabel(item.status)}</StatusBadge>{item.has_request_photo && <button className="button button-secondary" onClick={() => void showEvidence(item.id)}>Xem ảnh</button>}{item.status === "pending" && <><textarea aria-label="Lý do từ chối" placeholder="Bắt buộc nhập nếu từ chối" value={rejection[item.id] ?? ""} onChange={event => setRejection(current => ({ ...current, [item.id]: event.target.value }))} /><button className="button button-primary" onClick={() => void decide(item, "accepted")}>Chấp nhận · ghi nhận Muộn</button><button className="button button-danger" disabled={(rejection[item.id] ?? "").trim().length < 5} onClick={() => void decide(item, "rejected")}>Từ chối</button></>}</div>{item.status === "rejected" && item.reason && <p className="attendance-rejection">Lý do từ chối: {item.reason}</p>}</div></article>)}{!items.length && <p className="attendance-empty">Không có yêu cầu phù hợp với bộ lọc.</p>}</div>
    {preview && <div className="modal-backdrop" onClick={closePreview}><section className="attendance-photo-modal" role="dialog" aria-modal="true" onClick={event => event.stopPropagation()}><button onClick={closePreview}>Đóng</button><img src={preview} alt="Ảnh minh chứng điểm danh" /></section></div>}
  </div>;
}
function requestLabel(status: string) { return ({ pending: "Chờ xử lý", accepted: "Đã chấp nhận", rejected: "Đã từ chối" } as Record<string, string>)[status] ?? status; }
