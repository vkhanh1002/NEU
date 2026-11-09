"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { Camera, RefreshCw } from "lucide-react";
import { api } from "@/lib/api";
import { ErrorNotice, Loading, PageTitle, StatusBadge } from "@/components/ui";

type AttendanceItem = { record_id: string; session_id: string; course_code: string; course_name: string; section: string; starts_at: string; closed_at: string | null; session_status: string; status: string; evidence_id: string | null; evidence_received_at: string | null; makeup_request: { status: string; reason: string; submitted_at: string } | null; can_submit_request: boolean };
type AttendanceSummary = { completed_sessions: number; present: number; late: number; absent: number; participation_rate: number | null };

export function StudentAttendance() {
  const [items, setItems] = useState<AttendanceItem[]>([]); const [summary, setSummary] = useState<AttendanceSummary | null>(null); const [error, setError] = useState(""); const [busy, setBusy] = useState(false); const [loading, setLoading] = useState(true); const [stream, setStream] = useState<MediaStream | null>(null); const [active, setActive] = useState<AttendanceItem | null>(null); const [captured, setCaptured] = useState<Blob | null>(null); const video = useRef<HTMLVideoElement>(null); const canvas = useRef<HTMLCanvasElement>(null);
  const load = useCallback(async () => { try { const data = await api<{ items: AttendanceItem[]; summary: AttendanceSummary }>("/student/attendance"); setItems(data.items); setSummary(data.summary); } catch (reason) { setError(reason instanceof Error ? reason.message : "Không tải được lịch sử điểm danh."); } finally { setLoading(false); } }, []);
  useEffect(() => { void load(); }, [load]);
  useEffect(() => { if (video.current && stream) { video.current.srcObject = stream; void video.current.play(); } return () => { stream?.getTracks().forEach(track => track.stop()); }; }, [stream]);
  async function openCamera(item: AttendanceItem) {
    setError(""); setCaptured(null); setActive(item);
    try { if (!navigator.mediaDevices?.getUserMedia) throw new Error("Thiết bị hoặc trình duyệt không hỗ trợ camera trực tiếp."); setStream(await navigator.mediaDevices.getUserMedia({ video: { facingMode: { ideal: "environment" } }, audio: false })); }
    catch (cause) { setError(cause instanceof Error ? cause.message : "Không thể mở camera. Hãy cho phép quyền camera."); setActive(null); }
  }
  function closeCamera() { stream?.getTracks().forEach(track => track.stop()); setStream(null); setActive(null); setCaptured(null); }
  async function uploadEvidence(blob: Blob) {
    if (!active) return; setBusy(true); setError("");
    const form = new FormData(); form.append("photo", blob, "attendance-capture.jpg");
    try { await api(`/student/attendance/sessions/${active.session_id}/evidence`, { method: "POST", body: form }); closeCamera(); await load(); }
    catch (cause) { setCaptured(blob); setError(cause instanceof Error ? cause.message : "Không gửi được ảnh. Ảnh chụp vẫn đang được giữ để thử lại."); }
    finally { setBusy(false); }
  }
  function capture() {
    const element = video.current; const output = canvas.current;
    if (!element || !output || !element.videoWidth) { setError("Camera chưa sẵn sàng. Vui lòng chờ hình ảnh xuất hiện rồi chụp lại."); return; }
    const scale = Math.min(1, 1600 / Math.max(element.videoWidth, element.videoHeight));
    output.width = Math.round(element.videoWidth * scale); output.height = Math.round(element.videoHeight * scale);
    output.getContext("2d")?.drawImage(element, 0, 0, output.width, output.height);
    output.toBlob(blob => { if (blob) { setCaptured(blob); void uploadEvidence(blob); } else setError("Không tạo được ảnh từ camera."); }, "image/jpeg", .78);
  }
  async function requestMakeup(item: AttendanceItem) { setBusy(true); setError(""); try { await api(`/student/attendance/records/${item.record_id}/makeup-requests`, { method: "POST" }); await load(); } catch (cause) { setError(cause instanceof Error ? cause.message : "Không gửi được yêu cầu."); } finally { setBusy(false); } }
  return <div className="attendance-page student-attendance-page"><PageTitle eyebrow="KHÔNG GIAN SINH VIÊN" title="Lịch sử điểm danh" description="Theo dõi trạng thái từng buổi học, gửi ảnh từ camera trong giờ và yêu cầu điểm danh bù sau khi buổi học kết thúc." />{error && <ErrorNotice message={error} />}
    {!loading && summary && <section className="student-attendance-summary"><article><small>ĐÃ CHỐT ĐIỂM DANH</small><strong>{summary.completed_sessions}</strong></article><article><small>CÓ MẶT</small><strong>{summary.present}</strong></article><article><small>MUỘN</small><strong>{summary.late}</strong></article><article><small>VẮNG</small><strong>{summary.absent}</strong></article><article><small>TỶ LỆ THAM GIA</small><strong>{summary.participation_rate === null ? "—" : `${summary.participation_rate}%`}</strong></article></section>}
    {loading ? <Loading label="Đang tải lịch sử điểm danh…" /> : !items.length ? <p className="attendance-empty">Chưa có phiên điểm danh của các lớp bạn đăng ký.</p> : <div className="attendance-history student-attendance-list">{items.map(item => <article key={item.record_id}><div><small>{item.course_code} · {item.section}</small><h2>{item.course_name}</h2><p>{new Date(item.starts_at).toLocaleString("vi-VN")}</p>{item.evidence_received_at && <p>Máy chủ nhận ảnh: {new Date(item.evidence_received_at).toLocaleString("vi-VN")}</p>}{item.makeup_request && <p className={item.makeup_request.status === "rejected" ? "attendance-rejection" : "attendance-note"}>{requestLabel(item.makeup_request.status)}{item.makeup_request.reason ? ` · ${item.makeup_request.reason}` : ""}</p>}</div><StatusBadge>{item.session_status === "open" && item.status === "absent" ? "Phiên đang diễn ra" : attendanceLabel(item.status)}</StatusBadge><div className="student-attendance-actions">{item.session_status === "open" && !item.evidence_id && <button className="button button-primary" disabled={busy} onClick={() => void openCamera(item)}><Camera size={17} /> Chụp ảnh minh chứng</button>}{item.evidence_id && <span className="attendance-note">Đã nhận ảnh trong phiên học</span>}{item.can_submit_request && <button className="button button-secondary" disabled={busy} onClick={() => void requestMakeup(item)}>Yêu cầu điểm danh bù</button>}</div></article>)}</div>}
    {active && <div className="modal-backdrop"><section className="attendance-camera-modal" role="dialog" aria-modal="true" aria-label="Chụp ảnh minh chứng"><header><div><h2>Ảnh minh chứng trong giờ học</h2><p>{active.course_code} · {active.course_name}</p></div><button onClick={closeCamera}>Đóng</button></header><video ref={video} playsInline muted /><canvas ref={canvas} hidden /><p>Ảnh được gửi ngay khi chụp. Thời gian ghi nhận do máy chủ xác định.</p><div><button className="button button-primary" disabled={!stream || busy} onClick={capture}><Camera size={17} />{busy ? "Đang gửi ảnh…" : captured ? "Chụp lại và gửi" : "Chụp và gửi"}</button>{captured && <button className="button button-secondary" disabled={busy} onClick={() => void uploadEvidence(captured)}><RefreshCw size={16} /> Thử gửi lại ảnh đã chụp</button>}</div></section></div>}
  </div>;
}

function attendanceLabel(status: string) { return ({ present: "Có mặt", late: "Muộn", absent: "Vắng" } as Record<string, string>)[status] ?? status; }
function requestLabel(status: string) { return ({ pending: "Đang chờ giảng viên duyệt", accepted: "Đã chấp nhận — trạng thái Muộn", rejected: "Đã từ chối — vẫn tính Vắng" } as Record<string, string>)[status] ?? status; }
