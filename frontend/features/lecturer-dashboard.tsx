"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ArrowRight, CalendarDays, Camera, CircleAlert, UsersRound } from "lucide-react";
import { api } from "@/lib/api";
import { ErrorNotice, Loading, PageTitle } from "@/components/ui";

type Data = { lecturer: string; class_count: number; student_count: number; sessions_count: number; pending_requests: number; attendance_rate: number | null; today: { id: string; course: string; code: string; section: string; room: string; starts_at: string; ends_at: string }[] };

export function LecturerDashboard() {
  const [data, setData] = useState<Data | null>(null); const [error, setError] = useState("");
  useEffect(() => { api<Data>("/lecturer/overview").then(setData).catch(reason => setError(reason.message)); }, []);
  return <div className="lecturer-dashboard"><PageTitle eyebrow="KHÔNG GIAN GIẢNG VIÊN" title={`Xin chào${data?.lecturer ? `, ${data.lecturer.split(" ").slice(-1)[0]}` : ""}`} description="Lớp phụ trách, lịch giảng dạy và công việc cần xử lý." />{error && <ErrorNotice message={error} />}{!data && !error ? <Loading /> : data && <>
    <section className="lecturer-metrics"><article><UsersRound /><span>Lớp học phần</span><strong>{data.class_count}</strong></article><article><UsersRound /><span>Sinh viên đang dạy</span><strong>{data.student_count}</strong></article><article><Camera /><span>Phiên điểm danh</span><strong>{data.sessions_count}</strong></article><article><CircleAlert /><span>Yêu cầu chờ duyệt</span><strong>{data.pending_requests}</strong></article></section>
    <div className="lecturer-dashboard-grid"><section className="panel"><header><div><h2>Lịch dạy hôm nay</h2><p>Dựa trên các lớp được phân công trong học kỳ hiện tại.</p></div><CalendarDays /></header>{data.today.length ? data.today.map(item => <article className="lecturer-today-class" key={item.id}><time>{item.starts_at}–{item.ends_at}</time><div><strong>{item.code} · {item.section} — {item.course}</strong><small>{item.room || "Chưa xếp phòng"}</small></div><Link href="/lecturer/attendance">Điểm danh</Link></article>) : <p className="attendance-empty">Hôm nay không có lịch dạy theo thời khóa biểu hiện tại.</p>}</section><section className="panel lecturer-work-panel"><h2>Công việc</h2><Link href="/lecturer/attendance/requests"><span>{data.pending_requests}</span><div><strong>Yêu cầu điểm danh bù</strong><small>Giảng viên xem minh chứng và tự quyết định</small></div><ArrowRight /></Link><Link href="/lecturer/classes"><span>{data.class_count}</span><div><strong>Quản lý lớp học phần</strong><small>Tra cứu sinh viên trong phạm vi lớp phụ trách</small></div><ArrowRight /></Link><Link href="/lecturer/schedule"><span><CalendarDays /></span><div><strong>Thời khóa biểu</strong><small>Xem lịch dạy và chi tiết buổi học</small></div><ArrowRight /></Link></section></div>
    <p className="attendance-note">Chuyên cần tổng hợp: {data.attendance_rate === null ? "chưa có phiên đã chốt" : `${data.attendance_rate}% có mặt hoặc muộn`} · tính trên các phiên đã kết thúc.</p>
  </>}</div>;
}
