"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ArrowRight, CalendarDays, CircleHelp, FileText, GraduationCap, Plus, UsersRound } from "lucide-react";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { ErrorNotice, Loading, PageTitle, StatusBadge } from "@/components/ui";

type DashboardData = {
  year: number; students: number; applications: number; majors: number; pending_tickets: number;
  admissions_by_month: { month: string; applications: number }[];
  students_by_major: { name: string; students: number }[];
  recent_activity: { title: string; detail: string; at: string; kind: string }[];
};

export function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [error, setError] = useState("");
  const { user } = useAuth();
  useEffect(() => { api<DashboardData>("/dashboard").then(setData).catch(reason => setError(reason.message)); }, []);
  const canOpenProfiles = ["super_admin", "support_staff", "academic_staff"].includes(user?.role ?? "");
  const activityHref = user?.role === "support_staff" ? "/support" : "/admissions";
  const showActivityLink = ["super_admin", "admission_staff", "support_staff"].includes(user?.role ?? "");
  const quickActions: Record<string, { label: string; description: string; href: string; icon: typeof Plus; color: string }[]> = {
    super_admin: [
      { label: "Hồ sơ tuyển sinh", description: "Tiếp nhận và rà soát hồ sơ", href: "/admissions", icon: Plus, color: "blue" },
      { label: "Yêu cầu hỗ trợ", description: "Theo dõi yêu cầu người học", href: "/support", icon: CircleHelp, color: "green" },
      { label: "Hồ sơ sinh viên", description: "Tra cứu thông tin người học", href: "/profiles", icon: UsersRound, color: "blue" },
    ],
    admission_staff: [{ label: "Hồ sơ xét tuyển", description: "Xem và cập nhật hồ sơ", href: "/admissions", icon: FileText, color: "blue" }],
    support_staff: [
      { label: "Danh sách yêu cầu", description: "Theo dõi và phản hồi", href: "/support", icon: CircleHelp, color: "green" },
      { label: "Hồ sơ sinh viên", description: "Tra cứu thông tin người học", href: "/profiles", icon: UsersRound, color: "blue" },
    ],
    hr_staff: [
      { label: "Hồ sơ giảng viên", description: "Quản lý hồ sơ giảng viên", href: "/personnel/lecturers", icon: GraduationCap, color: "blue" },
      { label: "Hồ sơ nhân viên", description: "Quản lý hồ sơ nhân sự", href: "/personnel/employees", icon: UsersRound, color: "green" },
    ],
    academic_staff: [{ label: "Hồ sơ sinh viên", description: "Tra cứu thông tin người học", href: "/profiles", icon: UsersRound, color: "blue" }],
    lecturer: [
      { label: "Thời khóa biểu giảng dạy", description: "Xem các lớp học phần được phân công", href: "/lecturer/schedule", icon: CalendarDays, color: "blue" },
      { label: "Trợ lý học thuật", description: "Tra cứu tài liệu và hướng dẫn", href: "/assistant", icon: CircleHelp, color: "green" },
    ],
  };
  const actions = quickActions[user?.role ?? ""] ?? [];
  const canViewActivity = showActivityLink || (data?.recent_activity.length ?? 0) > 0;
  const date = new Intl.DateTimeFormat("vi-VN", { weekday: "long", day: "numeric", month: "long", year: "numeric" }).format(new Date());
  return <div className="dashboard-page">
    <PageTitle eyebrow="TỔNG QUAN" title={`Xin chào${user ? `, ${user.full_name.split(" ").slice(-1)[0]}` : ""} 👋`} description="Đây là những gì đang diễn ra trong hệ thống NEU hôm nay." action={<div className="today-label">{date}</div>} />
    {error && <ErrorNotice message={error} />}
    {!data && !error ? <Loading /> : <>
      <section className="stat-grid">
        <StatCard label="Tổng sinh viên" value={data?.students ?? 0} sub="Hồ sơ đang quản lý" icon={UsersRound} color="blue" />
        <StatCard label="Hồ sơ tuyển sinh" value={data?.applications ?? 0} sub="Tổng hồ sơ tiếp nhận" icon={FileText} color="blue" />
        <StatCard label="Ngành đào tạo" value={data?.majors ?? 0} sub="Danh mục trong hệ thống" icon={GraduationCap} color="green" />
        <StatCard label="Yêu cầu chờ xử lý" value={data?.pending_tickets ?? 0} sub="Trung tâm hỗ trợ" icon={CircleHelp} color="green" />
      </section>
      <section className="dashboard-grid">
        <div className="panel admissions-chart-panel"><div className="panel-heading"><div><h2>Hoạt động tuyển sinh</h2><p>Số hồ sơ theo tháng trong năm</p></div><span className="dashboard-year">{data?.year}</span></div><AdmissionsChart data={data?.admissions_by_month ?? []} /></div>
        <div className="panel majors-panel"><div className="panel-heading"><div><h2>Sinh viên theo ngành</h2><p>Phân bố hồ sơ sinh viên</p></div>{canOpenProfiles && <Link href="/profiles" className="panel-icon-link" aria-label="Mở hồ sơ"><ArrowRight size={17} /></Link>}</div><MajorChart data={data?.students_by_major ?? []} /></div>
      </section>
      <section className="dashboard-lower">
        <div className="panel activity-panel"><div className="panel-heading"><div><h2>Hoạt động gần đây</h2><p>Cập nhật mới nhất trên hệ thống</p></div>{canViewActivity && <Link className="text-button" href={activityHref}>Xem tất cả <ArrowRight size={15} /></Link>}</div>
          {(data?.recent_activity ?? []).length ? <div className="activity-list">{data!.recent_activity.map((item, index) => <div className="activity-item" key={`${item.title}-${index}`}><div className={`activity-avatar ${item.kind}`} aria-hidden>{item.kind === "support" ? <CircleHelp size={16} /> : <FileText size={16} />}</div><div className="activity-copy"><strong>{item.title}</strong><span>{new Date(item.at).toLocaleString("vi-VN", { dateStyle: "medium", timeStyle: "short" })}</span></div><StatusBadge>{item.detail}</StatusBadge></div>)}</div> : <div className="empty-inline">Chưa có hoạt động để hiển thị.</div>}
        </div>
        <div className="quick-panel"><div className="panel-heading"><div><h2>Thao tác nhanh</h2><p>Đi đến nghiệp vụ theo quyền truy cập</p></div></div>
          {actions.map(action => <Link className="quick-action" href={action.href} key={action.href}><span className={`quick-icon ${action.color}`}><action.icon size={18} /></span><span><strong>{action.label}</strong><small>{action.description}</small></span><ArrowRight size={16} /></Link>)}
        </div>
      </section>
    </>}
  </div>;
}

function StatCard({ label, value, sub, icon: Icon, color }: { label: string; value: number; sub: string; icon: typeof UsersRound; color: string }) {
  return <article className="stat-card"><div className="stat-card-top"><span>{label}</span><span className={`stat-icon ${color}`}><Icon size={18} /></span></div><div className="stat-value">{value.toLocaleString("vi-VN")}</div><div className="stat-footer"><span>{sub}</span></div></article>;
}

function AdmissionsChart({ data }: { data: DashboardData["admissions_by_month"] }) {
  if (!data.length) return <div className="chart-empty">Chưa có dữ liệu.</div>;
  const max = Math.max(...data.map(item => item.applications), 1);
  const points = data.map((item, index) => ({ x: 42 + index * 49, y: 160 - (item.applications / max) * 125, ...item }));
  const line = points.map(point => `${point.x},${point.y}`).join(" ");
  return <div className="line-chart-wrap"><div className="chart-legend"><span><i /> Hồ sơ tiếp nhận</span><small>Tổng theo tháng</small></div><svg viewBox="0 0 610 205" role="img" aria-label="Biểu đồ hồ sơ tuyển sinh theo tháng" className="line-chart"><defs><linearGradient id="line-fill" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stopColor="#66aef4" stopOpacity=".22" /><stop offset="1" stopColor="#66aef4" stopOpacity="0" /></linearGradient></defs>{[35, 75, 115, 155].map(y => <line key={y} x1="30" x2="590" y1={y} y2={y} stroke="#edf1f5" strokeDasharray="4 5" />)}<polygon points={`42,160 ${line} 581,160`} fill="url(#line-fill)"/><polyline points={line} fill="none" stroke="#358bd9" strokeWidth="3" strokeLinejoin="round" strokeLinecap="round"/>{points.map(point => <g key={point.month}><circle cx={point.x} cy={point.y} r="3.5" fill="#fff" stroke="#358bd9" strokeWidth="2"/><text x={point.x} y="188" textAnchor="middle" fill="#8995a4" fontSize="10">{point.month}</text></g>)}</svg></div>;
}

const chartColors = ["#398fdd", "#80c7aa", "#246da7", "#46a383", "#7cc4d2", "#b5d8eb"];
function MajorChart({ data }: { data: DashboardData["students_by_major"] }) {
  const total = data.reduce((sum, row) => sum + row.students, 0);
  let start = 0;
  const slices = data.map((row, index) => {
    const percent = total ? row.students / total : 0;
    const dash = percent * 251.2;
    const slice = { ...row, color: chartColors[index % chartColors.length], dash, offset: -start };
    start += dash;
    return slice;
  });
  return <div className="major-chart"><div className="donut-wrap"><svg viewBox="0 0 120 120" role="img" aria-label="Phân bố sinh viên theo ngành"><circle cx="60" cy="60" r="40" fill="none" stroke="#f0f3f6" strokeWidth="15" />{slices.map((slice, index) => <circle key={slice.name} cx="60" cy="60" r="40" fill="none" stroke={slice.color} strokeWidth="15" strokeDasharray={`${slice.dash} ${251.2 - slice.dash}`} strokeDashoffset={slice.offset} transform="rotate(-90 60 60)" className="donut-segment" />)}</svg><div className="donut-center"><strong>{total}</strong><small>tổng SV</small></div></div>
    <div className="major-legend">{slices.length ? slices.map(slice => <div key={slice.name}><span className="legend-dot" style={{ background: slice.color }} /><span className="legend-name">{slice.name}</span><strong>{slice.students}</strong></div>) : <span className="muted-text">Chưa có dữ liệu hồ sơ</span>}</div></div>;
}
