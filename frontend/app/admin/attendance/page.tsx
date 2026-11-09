"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { ErrorNotice, Loading, PageTitle, StatusBadge } from "@/components/ui";

type Session = { id: string; course_code: string; course_name: string; section: string; starts_at: string; status: string; present: number; late: number; absent: number; total: number };
type Audit = { id: string; session_id: string; actor_id: string; action: string; details: Record<string, unknown>; created_at: string };
type Request = { id: string; status: string; reason: string; student_number: string; student_name: string; course_code: string; course_name: string; section: string; session_id: string; evidence_id: string; submitted_at: string; reviewed_at: string | null; reviewed_by: string | null; attendance_status: string };
export default function AdminAttendancePage() {
  const [data, setData] = useState<{ sessions: Session[]; requests: Request[]; audit: Audit[] } | null>(null); const [error, setError] = useState("");
  useEffect(() => { api<{ sessions: Session[]; requests: Request[]; audit: Audit[] }>("/admin/attendance").then(setData).catch(reason => setError(reason.message)); }, []);
  return <div className="attendance-page"><PageTitle eyebrow="QUẢN TRỊ" title="Giám sát điểm danh" description="Tra cứu phiên điểm danh, yêu cầu, trạng thái chuyên cần và lịch sử thay đổi." />{error && <ErrorNotice message={error} />}{!data && !error ? <Loading /> : <><div className="attendance-history">{data?.sessions.map(item => <article key={item.id}><div><small>{item.course_code} · {item.section}</small><h2>{item.course_name}</h2><p>{new Date(item.starts_at).toLocaleString("vi-VN")}</p></div><StatusBadge>{item.status === "open" ? "Đang diễn ra" : "Đã kết thúc"}</StatusBadge><span>Có mặt {item.present} · Muộn {item.late} · Vắng {item.absent} / {item.total}</span></article>)}</div><section className="attendance-admin-audit"><h2>Yêu cầu điểm danh bù</h2>{data?.requests.map(item => <article key={item.id}><time>{new Date(item.submitted_at).toLocaleString("vi-VN")}</time><strong>{item.student_name} · {item.student_number}</strong><span>{item.course_code} · {item.section} · {requestLabel(item.status)} · Điểm danh: {item.attendance_status}</span>{item.reason && <span>{item.reason}</span>}<code>{item.evidence_id}</code></article>)}</section><section className="attendance-admin-audit"><h2>Lịch sử xử lý gần đây</h2>{data?.audit.map(item => <article key={item.id}><time>{new Date(item.created_at).toLocaleString("vi-VN")}</time><strong>{auditLabel(item.action)}</strong><code>{item.session_id}</code></article>)}</section></>}</div>;
}
function auditLabel(action: string) { return ({ session_opened: "Mở phiên", session_closed: "Kết thúc phiên", evidence_received: "Nhận ảnh minh chứng", makeup_requested: "Gửi yêu cầu điểm danh bù", makeup_accepted: "Chấp nhận điểm danh bù", makeup_rejected: "Từ chối điểm danh bù", record_marked: "Cập nhật trạng thái" } as Record<string, string>)[action] ?? action; }
function requestLabel(status: string) { return ({ pending: "Chờ duyệt", accepted: "Đã chấp nhận", rejected: "Đã từ chối" } as Record<string, string>)[status] ?? status; }
