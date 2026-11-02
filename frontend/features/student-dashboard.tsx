"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { Award, Bell, BookOpen, CalendarDays, ChevronRight, CircleHelp, ClipboardList, Clock3, Wallet } from "lucide-react";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { EmptyState, ErrorNotice, Loading, PageTitle } from "@/components/ui";

type Overview = {
  student: { student_number: string; full_name: string; email: string; major_name: string; class_name: string; cohort: string; study_status: string; enrollment_date: string | null };
  current_semester: { code: string; name: string; academic_year: string } | null;
  credits_earned: number; credits_required: number; gpa: number | null; outstanding_amount: number;
  conduct: { score: number; rating: string; semester: string } | null;
  current_courses: { offering_id: string; course_code: string; course_name: string; credits: number; weekday: number; starts_at: string; ends_at: string; room: string; lecturer: string }[];
  upcoming_exams: { course_name: string; starts_at_datetime: string; room: string }[];
  upcoming_assignments: { id: string; title: string; course_name: string; deadline: string; status: string }[];
  failed_courses: { course_code: string; course_name: string; semester: string; total_score: number }[];
};
type Notices = { items: { id: string; title: string; message: string; href: string; created_at: string; read_at: string | null }[]; unread_count: number };
const learningLinks = [
  { label: "Thời khóa biểu", detail: "Lịch học theo tuần", href: "/student/schedule", icon: CalendarDays },
  { label: "Lịch thi", detail: "Lịch thi và phòng thi", href: "/student/exams", icon: Clock3 },
  { label: "Kết quả học tập", detail: "Điểm số và tín chỉ", href: "/student/results", icon: BookOpen },
  { label: "Kết quả rèn luyện", detail: "Theo dõi đánh giá học kỳ", href: "/student/conduct", icon: Award },
  { label: "Tài chính sinh viên", detail: "Khoản thu và giao dịch", href: "/student/finance", icon: Wallet },
  { label: "Bài tập và hạn nộp", detail: "Công việc môn học", href: "/student/assignments", icon: ClipboardList },
];

export function StudentStudyDashboard() {
  const { user } = useAuth();
  const [overview, setOverview] = useState<Overview | null>(null);
  const [notices, setNotices] = useState<Notices | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const load = useCallback(async () => {
    setLoading(true); setError("");
    try {
      const [data, notificationRows] = await Promise.all([api<Overview>("/student/overview"), api<Notices>("/notifications")]);
      setOverview(data); setNotices(notificationRows);
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Chưa tải được thông tin học tập."); }
    finally { setLoading(false); }
  }, []);
  useEffect(() => { void load(); }, [load]);
  const name = overview?.student.full_name || user?.full_name || "Sinh viên";
  return <div className="student-dashboard">
    <PageTitle eyebrow="KHÔNG GIAN SINH VIÊN" title={`Chào ${name.split(" ").slice(-1)[0]} 👋`} description="Tiến độ học tập và các dịch vụ dành cho người học." action={<span className="student-term">{overview?.current_semester?.name ?? "Chưa có học kỳ hiện tại"}</span>} />
    {error && <ErrorNotice message={error} />}
    {loading ? <Loading label="Đang tải hồ sơ và dữ liệu học tập…" /> : !overview ? <EmptyState icon={<CircleHelp size={22} />} title="Chưa có hồ sơ sinh viên liên kết" description="Tài khoản này chưa được gắn với hồ sơ sinh viên. Vui lòng liên hệ bộ phận đào tạo để được hỗ trợ." /> : <>
      <section className="student-profile-strip"><div className="student-avatar">{name.slice(0, 1)}</div><div><small>HỒ SƠ SINH VIÊN</small><strong>{name}</strong><span>{overview.student.student_number} · {overview.student.major_name} · {overview.student.class_name} · {overview.student.study_status}</span></div><Link href="/profiles">Thông tin cá nhân <ChevronRight size={15} /></Link></section>
      <section className="student-stat-grid">
        <StudentMetric label="Tín chỉ tích lũy" value={`${overview.credits_earned} / ${overview.credits_required}`} note="Theo các học phần đã đạt" icon={BookOpen} />
        <StudentMetric label="GPA tích lũy" value={overview.gpa?.toFixed(2) ?? "—"} note="Thang điểm 4.0" icon={Award} />
        <StudentMetric label="Khoản còn phải nộp" value={money(overview.outstanding_amount)} note="Tổng hợp từ sổ tài chính" icon={Wallet} />
        <StudentMetric label="Thông báo chưa đọc" value={String(notices?.unread_count ?? 0)} note="Thông báo theo tài khoản" icon={Bell} />
      </section>
      <div className="student-main-grid">
        <section className="student-panel"><div className="student-panel-heading"><div><small>HỌC TẬP</small><h2>Dịch vụ học tập</h2></div><BookOpen size={18} /></div><div className="student-service-list">{learningLinks.map(item => <Link href={item.href} key={item.href}><span><item.icon size={17} /></span><div><strong>{item.label}</strong><small>{item.detail}</small></div><ChevronRight size={15} /></Link>)}</div></section>
        <section className="student-panel"><div className="student-panel-heading"><div><small>CẬP NHẬT</small><h2>Thông báo gần đây</h2></div><Bell size={18} /></div>{notices?.items.length ? <div className="student-notice-list">{notices.items.slice(0, 5).map(item => <Link href={item.href} key={item.id} className={item.read_at ? "" : "unread"}><span /><div><strong>{item.title}</strong><p>{item.message}</p><small>{new Date(item.created_at).toLocaleDateString("vi-VN")}</small></div></Link>)}</div> : <div className="student-empty"><CircleHelp size={20} /><strong>Chưa có thông báo</strong><span>Thông báo quan trọng sẽ xuất hiện tại đây.</span></div>}</section>
      </div>
      <div className="student-main-grid student-detail-grid">
        <section className="student-panel"><div className="student-panel-heading"><div><small>HỌC KỲ HIỆN TẠI</small><h2>Học phần đang theo học</h2></div><CalendarDays size={18} /></div>{overview.current_courses.length ? <div className="student-course-list">{overview.current_courses.map(course => <article key={course.offering_id}><div><strong>{course.course_name}</strong><small>{course.course_code} · {course.credits} tín chỉ · {course.lecturer}</small></div><span>Thứ {course.weekday}, {course.starts_at}–{course.ends_at} · {course.room}</span></article>)}</div> : <div className="student-empty">Chưa có học phần trong học kỳ này.</div>}</section>
        <section className="student-panel"><div className="student-panel-heading"><div><small>SẮP TỚI</small><h2>Lịch thi và hạn nộp</h2></div><Clock3 size={18} /></div><div className="student-upcoming-list">{overview.upcoming_exams.slice(0, 3).map((exam, index) => <article key={`exam-${index}`}><strong>Lịch thi · {exam.course_name}</strong><small>{new Date(exam.starts_at_datetime).toLocaleString("vi-VN")} · {exam.room}</small></article>)}{overview.upcoming_assignments.slice(0, 3).map(task => <article key={task.id}><strong>{task.title}</strong><small>{task.course_name} · Hạn {new Date(task.deadline).toLocaleString("vi-VN")}</small></article>)}{!overview.upcoming_exams.length && !overview.upcoming_assignments.length && <EmptyState title="Chưa có lịch sắp tới" description="Lịch thi và hạn nộp sẽ xuất hiện tại đây." />}</div></section>
      </div>
      {overview.failed_courses.length > 0 && <section className="student-panel student-failed-panel"><div className="student-panel-heading"><div><small>CẦN THEO DÕI</small><h2>Học phần chưa đạt</h2></div></div>{overview.failed_courses.map(course => <p key={`${course.course_code}-${course.semester}`}>{course.course_code} · {course.course_name} · {course.semester} · {course.total_score}/10</p>)}</section>}
      <div className="student-data-note">Kết quả và lịch biểu được tải theo hồ sơ của tài khoản đang đăng nhập. Số liệu tài chính trên hệ thống chỉ phục vụ theo dõi quy trình, không tạo giao dịch thanh toán thật.</div>
    </>}
  </div>;
}

function StudentMetric({ label, value, note, icon: Icon }: { label: string; value: string; note: string; icon: typeof BookOpen }) {
  return <article className="student-metric"><span><Icon size={17} /></span><small>{label}</small><strong>{value}</strong><p>{note}</p></article>;
}

function money(value: number) { return new Intl.NumberFormat("vi-VN", { style: "currency", currency: "VND", maximumFractionDigits: 0 }).format(value); }
