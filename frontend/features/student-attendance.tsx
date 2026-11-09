"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { Camera, RefreshCw } from "lucide-react";
import { api } from "@/lib/api";
import { ErrorNotice, Loading, PageTitle, StatusBadge } from "@/components/ui";

type Makeup = { status: string; reason: string; request_reason: string; submitted_at: string; photo_captured_at?: string | null } | null;
type AttendanceItem = { record_id: string; session_id: string; course_code: string; course_name: string; section: string; lecturer_name: string; room: string; starts_at: string; closed_at: string | null; session_status: string; status: string; evidence_id: string | null; evidence_received_at: string | null; makeup_request: Makeup; can_submit_request: boolean };
type Summary = { completed_sessions: number; present: number; late: number; absent: number; participation_rate: number | null };

export function StudentAttendance() {
  const [items, setItems] = useState<AttendanceItem[]>([]); const [summary, setSummary] = useState<Summary | null>(null);
  const [error, setError] = useState(""); const [historyLoadFailed, setHistoryLoadFailed] = useState(false);
  const [busy, setBusy] = useState(false); const [loading, setLoading] = useState(true);
  const [stream, setStream] = useState<MediaStream | null>(null); const [active, setActive] = useState<AttendanceItem | null>(null);
  const [captured, setCaptured] = useState<Blob | null>(null); const [previewUrl, setPreviewUrl] = useState("");
  const [requesting, setRequesting] = useState<AttendanceItem | null>(null); const [requestReason, setRequestReason] = useState("");
  const [makeupStream, setMakeupStream] = useState<MediaStream | null>(null);
  const [makeupPhoto, setMakeupPhoto] = useState<Blob | null>(null); const [makeupPhotoUrl, setMakeupPhotoUrl] = useState("");
  const [makeupCapturedAt, setMakeupCapturedAt] = useState("");
  const video = useRef<HTMLVideoElement>(null); const canvas = useRef<HTMLCanvasElement>(null);
  const makeupVideo = useRef<HTMLVideoElement>(null); const makeupCanvas = useRef<HTMLCanvasElement>(null);
  const load = useCallback(async () => {
    setLoading(true); setHistoryLoadFailed(false); setError("");
    try { const data = await api<{ items: AttendanceItem[]; summary: Summary }>("/student/attendance"); setItems(data.items); setSummary(data.summary); }
    catch (cause) { setHistoryLoadFailed(true); setError(cause instanceof Error ? cause.message : "Không tải được lịch sử điểm danh."); }
    finally { setLoading(false); }
  }, []);
  useEffect(() => { void load(); }, [load]);
  useEffect(() => { if (video.current && stream) { video.current.srcObject = stream; void video.current.play(); } }, [stream]);
  useEffect(() => { if (makeupVideo.current && makeupStream) { makeupVideo.current.srcObject = makeupStream; void makeupVideo.current.play(); } }, [makeupStream]);
  useEffect(() => () => { stream?.getTracks().forEach(track => track.stop()); }, [stream]);
  useEffect(() => () => { makeupStream?.getTracks().forEach(track => track.stop()); }, [makeupStream]);
  useEffect(() => () => { if (previewUrl) URL.revokeObjectURL(previewUrl); }, [previewUrl]);
  useEffect(() => () => { if (makeupPhotoUrl) URL.revokeObjectURL(makeupPhotoUrl); }, [makeupPhotoUrl]);
  async function openCamera(item: AttendanceItem) {
    setError(""); setCaptured(null); setActive(item);
    try { if (!navigator.mediaDevices?.getUserMedia) throw new Error("Thiết bị hoặc trình duyệt không hỗ trợ camera trực tiếp."); setStream(await navigator.mediaDevices.getUserMedia({ video: { facingMode: { ideal: "environment" } }, audio: false })); }
    catch (cause) { setError(cause instanceof Error ? cause.message : "Không thể mở camera. Hãy cho phép quyền camera."); setActive(null); }
  }
  function closeCamera() { stream?.getTracks().forEach(track => track.stop()); setStream(null); setActive(null); setCaptured(null); setPreviewUrl(""); }
  function capture() {
    const element = video.current; const output = canvas.current;
    if (!element || !output || !element.videoWidth) { setError("Camera chưa sẵn sàng. Vui lòng chờ hình ảnh xuất hiện rồi chụp lại."); return; }
    const scale = Math.min(1, 1600 / Math.max(element.videoWidth, element.videoHeight));
    output.width = Math.round(element.videoWidth * scale); output.height = Math.round(element.videoHeight * scale);
    output.getContext("2d")?.drawImage(element, 0, 0, output.width, output.height);
    output.toBlob(blob => { if (!blob) { setError("Không tạo được ảnh từ camera."); return; } setCaptured(blob); setPreviewUrl(URL.createObjectURL(blob)); }, "image/jpeg", .78);
  }
  async function openMakeupCamera() {
    setError("");
    try {
      if (!navigator.mediaDevices?.getUserMedia) throw new Error("Thiết bị hoặc trình duyệt không hỗ trợ camera trực tiếp.");
      setMakeupStream(await navigator.mediaDevices.getUserMedia({ video: { facingMode: { ideal: "environment" } }, audio: false }));
    } catch (cause) { setError(cause instanceof Error ? cause.message : "Không thể mở camera. Hãy cho phép quyền camera."); }
  }
  function stopMakeupCamera() { makeupStream?.getTracks().forEach(track => track.stop()); setMakeupStream(null); }
  function captureMakeupPhoto() {
    const element = makeupVideo.current; const output = makeupCanvas.current;
    if (!element || !output || !element.videoWidth) { setError("Camera chưa sẵn sàng. Hãy chờ hình ảnh xuất hiện rồi chụp lại."); return; }
    const scale = Math.min(1, 1600 / Math.max(element.videoWidth, element.videoHeight));
    output.width = Math.round(element.videoWidth * scale); output.height = Math.round(element.videoHeight * scale);
    output.getContext("2d")?.drawImage(element, 0, 0, output.width, output.height);
    output.toBlob(blob => {
      if (!blob) { setError("Không tạo được ảnh từ camera."); return; }
      if (makeupPhotoUrl) URL.revokeObjectURL(makeupPhotoUrl);
      setMakeupPhoto(blob); setMakeupPhotoUrl(URL.createObjectURL(blob)); setMakeupCapturedAt(new Date().toISOString());
      stopMakeupCamera(); setError("");
    }, "image/jpeg", .82);
  }
  function clearMakeupPhoto() {
    if (makeupPhotoUrl) URL.revokeObjectURL(makeupPhotoUrl);
    setMakeupPhoto(null); setMakeupPhotoUrl(""); setMakeupCapturedAt("");
  }
  function closeMakeupRequest() {
    stopMakeupCamera(); clearMakeupPhoto(); setRequesting(null); setRequestReason("");
  }
  async function submitEvidence() {
    if (!active || !captured) return;
    setBusy(true); setError(""); const form = new FormData(); form.append("photo", captured, "attendance-capture.jpg");
    try { await api(`/student/attendance/sessions/${active.session_id}/evidence`, { method: "POST", body: form }); closeCamera(); await load(); }
    catch (cause) { setError(cause instanceof Error ? cause.message : "Không gửi được ảnh minh chứng."); }
    finally { setBusy(false); }
  }
  async function submitMakeup() {
    if (!requesting || !makeupPhoto) { setError("Hãy chụp ảnh trực tiếp trước khi gửi yêu cầu."); return; }
    if (requestReason.trim().length < 10) { setError("Vui lòng nhập lý do ít nhất 10 ký tự."); return; }
    setBusy(true); setError(""); const form = new FormData();
    form.append("photo", makeupPhoto, "makeup-request.jpg"); form.append("reason", requestReason.trim());
    form.append("captured_at", makeupCapturedAt);
    try { await api(`/student/attendance/records/${requesting.record_id}/makeup-requests`, { method: "POST", body: form }); closeMakeupRequest(); await load(); }
    catch (cause) { setError(cause instanceof Error ? cause.message : "Không gửi được yêu cầu."); }
    finally { setBusy(false); }
  }
  return <div className="attendance-page student-attendance-page"><PageTitle eyebrow="KHÔNG GIAN SINH VIÊN" title="Lịch sử điểm danh" description="Xem trạng thái từng buổi, chụp ảnh trực tiếp trong giờ và gửi yêu cầu sau khi phiên kết thúc." />{error && <div className="attendance-load-error"><ErrorNotice message={error} />{historyLoadFailed && <button className="button button-secondary" disabled={loading} onClick={() => void load()}>{loading ? "Đang thử lại…" : "Thử lại"}</button>}</div>}
    {!loading && summary && <section className="student-attendance-summary"><article><small>ĐÃ CHỐT</small><strong>{summary.completed_sessions}</strong></article><article><small>CÓ MẶT</small><strong>{summary.present}</strong></article><article><small>MUỘN</small><strong>{summary.late}</strong></article><article><small>VẮNG</small><strong>{summary.absent}</strong></article><article><small>TỶ LỆ THAM GIA</small><strong>{summary.participation_rate === null ? "—" : `${summary.participation_rate}%`}</strong></article></section>}
    {loading ? <Loading label="Đang tải lịch sử điểm danh…" /> : historyLoadFailed && !items.length ? <p className="attendance-empty">Chưa thể tải lịch sử điểm danh. Hãy thử lại khi Backend kết nối được.</p> : !items.length ? <p className="attendance-empty">Chưa có phiên điểm danh của các lớp bạn đăng ký.</p> : <div className="attendance-history student-attendance-list">{items.map(item => <article key={item.record_id}><div><small>{item.course_code} · {item.section}</small><h2>{item.course_name}</h2><p>{new Date(item.starts_at).toLocaleString("vi-VN")} · {item.room || "Chưa xếp phòng"}</p><p>Giảng viên: {item.lecturer_name || "—"}</p>{item.evidence_received_at && <p>Hệ thống nhận ảnh: {new Date(item.evidence_received_at).toLocaleString("vi-VN")}</p>}{item.makeup_request && <div className="attendance-note"><strong>{requestLabel(item.makeup_request.status)}</strong><p>Lý do gửi: {item.makeup_request.request_reason}</p>{item.makeup_request.photo_captured_at && <small>Ảnh chụp lúc: {new Date(item.makeup_request.photo_captured_at).toLocaleString("vi-VN")}</small>}{item.makeup_request.reason && <p>Lý do xử lý: {item.makeup_request.reason}</p>}<small>Gửi lúc {new Date(item.makeup_request.submitted_at).toLocaleString("vi-VN")}</small></div>}</div><StatusBadge>{item.session_status === "open" && item.status === "absent" ? "Phiên đang diễn ra" : attendanceLabel(item.status)}</StatusBadge><div className="student-attendance-actions">{item.session_status === "open" && item.status === "absent" && !item.evidence_id && <button className="button button-primary" disabled={busy} onClick={() => void openCamera(item)}><Camera size={17} /> Chụp ảnh minh chứng</button>}{item.evidence_id && <span className="attendance-note">Đã nhận ảnh trong phiên học</span>}{item.can_submit_request && <button className="button button-secondary" disabled={busy} onClick={() => { setError(""); setRequestReason(""); clearMakeupPhoto(); setRequesting(item); }}>Yêu cầu điểm danh bù</button>}</div></article>)}</div>}
    {active && <div className="modal-backdrop"><section className="attendance-camera-modal" role="dialog" aria-modal="true" aria-label="Chụp ảnh minh chứng"><header><div><h2>Ảnh minh chứng trực tiếp</h2><p>{active.course_code} · {active.course_name} · {active.section}</p></div><button onClick={closeCamera}>Đóng</button></header><video ref={video} playsInline muted />{captured && previewUrl && <figure className="attendance-capture-figure"><figcaption>Ảnh vừa chụp — xem lại trước khi gửi</figcaption><img className="attendance-capture-preview" src={previewUrl} alt="Ảnh vừa chụp từ camera" /></figure>}<canvas ref={canvas} hidden /><p>Ảnh chỉ được ghi nhận nếu máy chủ nhận trong thời gian phiên còn mở.</p><div><button className="button button-secondary" disabled={!stream || busy} onClick={capture}><Camera size={17} />{captured ? "Chụp lại" : "Chụp ảnh"}</button>{captured && <button className="button button-primary" disabled={busy} onClick={() => void submitEvidence()}>{busy ? "Đang gửi…" : "Xác nhận gửi ảnh"}</button>}{captured && <button className="button button-ghost" disabled={busy} onClick={() => { setCaptured(null); setPreviewUrl(""); }}>Hủy ảnh</button>}</div></section></div>}
    {requesting && <div className="modal-backdrop" onClick={() => !busy && closeMakeupRequest()}><section className="form-modal makeup-request-modal" role="dialog" aria-modal="true" aria-labelledby="makeup-title" onClick={event => event.stopPropagation()}><header><div><h2 id="makeup-title">Yêu cầu điểm danh bù</h2><p>{requesting.course_code} · {requesting.section}</p></div><button onClick={closeMakeupRequest} disabled={busy} aria-label="Đóng">×</button></header><div className="makeup-photo-field"><canvas ref={makeupCanvas} hidden />{makeupPhotoUrl ? <><img className="attendance-capture-preview makeup-request-photo" src={makeupPhotoUrl} alt="Ảnh vừa chụp cho yêu cầu điểm danh bù" /><p>Thời điểm chụp: {new Date(makeupCapturedAt).toLocaleString("vi-VN")}</p><button type="button" className="button button-secondary" disabled={busy} onClick={() => { clearMakeupPhoto(); void openMakeupCamera(); }}>Chụp lại</button></> : makeupStream ? <><video ref={makeupVideo} playsInline muted /><button type="button" className="button button-primary" disabled={busy} onClick={captureMakeupPhoto}><Camera size={17} /> Chụp ảnh trực tiếp</button></> : <button type="button" className="button button-secondary" disabled={busy} onClick={() => void openMakeupCamera()}><Camera size={17} /> Mở camera</button>}</div><label>Lý do xin điểm danh bù *<textarea rows={3} maxLength={2000} value={requestReason} onChange={event => setRequestReason(event.target.value)} placeholder="Nhập lý do (ít nhất 10 ký tự)." /></label><div className="modal-actions"><button className="button button-ghost" disabled={busy} onClick={closeMakeupRequest}>Hủy</button><button className="button button-primary" disabled={busy || !makeupPhoto || requestReason.trim().length < 10} onClick={() => void submitMakeup()}>{busy ? "Đang gửi…" : "Gửi yêu cầu"}</button></div></section></div>}
  </div>;
}

function attendanceLabel(status: string) { return ({ present: "Có mặt", late: "Muộn", absent: "Vắng" } as Record<string, string>)[status] ?? status; }
function requestLabel(status: string) { return ({ pending: "Chờ giảng viên xác nhận", accepted: "Đã chấp nhận", rejected: "Đã từ chối" } as Record<string, string>)[status] ?? status; }
