"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ArrowDownRight, ArrowRight, ArrowUpRight, Bot, Calendar, CalendarCheck2, CircleHelp, Clock, FileText, GraduationCap, Plus, Sparkles, UsersRound } from "lucide-react";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { DemoTag, ErrorNotice, Loading, PageTitle, StatusBadge } from "@/components/ui";

type DashboardData = {
  students: number; applications: number; majors: number; pending_tickets: number;
  admissions_by_month: { month: string; applications: number }[];
  students_by_major: { name: string; students: number }[];
  recent_activity: { title: string; detail: string; at: string; kind: string }[];
  demo_data: boolean;
};

const emptyData: DashboardData = { students: 0, applications: 0, majors: 0, pending_tickets: 0, admissions_by_month: [], students_by_major: [], recent_activity: [], demo_data: true };

export function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [studySummary, setStudySummary] = useState<{ upcoming_deadlines: number; upcoming_exams: number; tasks: any[] } | null>(null);
  const [error, setError] = useState("");
  const { user } = useAuth();
  useEffect(() => {
    api<DashboardData>("/dashboard").then(setData).catch(reason => setError(reason.message));
    if (user) {
      api<{ upcoming_deadlines: number; upcoming_exams: number; tasks: any[] }>("/study/summary")
        .then(setStudySummary)
        .catch(() => {});
    }
  }, [user]);
  const date = new Intl.DateTimeFormat("vi-VN", { weekday: "long", day: "numeric", month: "long", year: "numeric" }).format(new Date());
  return <div className="dashboard-page">
    <PageTitle eyebrow="TỔNG QUAN" title={`Xin chào${user ? `, ${user.full_name.split(" ").slice(-1)[0]}` : ""} 👋`} description="Đây là những gì đang diễn ra trong Study hôm nay." action={<div className="today-label">{date}</div>} />
    {data?.demo_data && <div className="demo-banner"><span className="demo-banner-dot" /><span>Không gian demo — số liệu và thông tin ngành dưới đây chỉ phục vụ minh họa, không phải số liệu chính thức của một trường đại học.</span><DemoTag /></div>}
    {error && <ErrorNotice message={error} />}
    {!data && !error ? <Loading /> : <>
      <section className="stat-grid">
        <StatCard label="Tổng sinh viên" value={data?.students ?? 0} sub="Hồ sơ đang quản lý" icon={UsersRound} color="blue" trend="+8.2%" up />
        <StatCard label="Hồ sơ tuyển sinh" value={data?.applications ?? 0} sub="Tổng hồ sơ tiếp nhận" icon={FileText} color="violet" trend="+12.4%" up />
        <StatCard label="Ngành đào tạo" value={data?.majors ?? 0} sub="Đang hiển thị tuyển sinh" icon={GraduationCap} color="green" trend="10 ngành demo" />
        <StatCard label="Yêu cầu chờ xử lý" value={data?.pending_tickets ?? 0} sub="Trung tâm hỗ trợ" icon={CircleHelp} color="amber" trend="Cần theo dõi" />
      </section>
      <section className="dashboard-grid">
        <div className="panel admissions-chart-panel"><div className="panel-heading"><div><h2>Hoạt động tuyển sinh</h2><p>Số hồ sơ theo tháng trong năm</p></div><select aria-label="Chọn năm" defaultValue="2026"><option>2026</option><option>2025</option></select></div><AdmissionsChart data={data?.admissions_by_month ?? []} /></div>
        <div className="panel majors-panel"><div className="panel-heading"><div><h2>Sinh viên theo ngành</h2><p>Phân bố hồ sơ sinh viên</p></div><Link href="/profiles" className="panel-icon-link" aria-label="Mở hồ sơ"><ArrowRight size={17} /></Link></div><MajorChart data={data?.students_by_major ?? []} /></div>
      </section>
      <section className="dashboard-lower">
        <div className="panel activity-panel"><div className="panel-heading"><div><h2>Hoạt động gần đây</h2><p>Cập nhật mới nhất trên hệ thống</p></div><button className="text-button" onClick={() => window.location.assign("/admissions")}>Xem tất cả <ArrowRight size={15} /></button></div>
          {(data?.recent_activity ?? []).length ? <div className="activity-list">{data!.recent_activity.map((item, index) => <div className="activity-item" key={`${item.title}-${index}`}><div className={`activity-avatar ${item.kind}`} aria-hidden>{item.kind === "support" ? <CircleHelp size={16} /> : <FileText size={16} />}</div><div className="activity-copy"><strong>{item.title}</strong><span>{new Date(item.at).toLocaleString("vi-VN", { dateStyle: "medium", timeStyle: "short" })}</span></div><StatusBadge>{item.detail}</StatusBadge></div>)}</div> : <div className="empty-inline">Chưa có hoạt động để hiển thị.</div>}
        </div>
        <div className="quick-panel"><div className="panel-heading"><div><h2>Thao tác nhanh</h2><p>Đi đến nghiệp vụ thường dùng</p></div></div>
          <Link className="quick-action" href="/admissions"><span className="quick-icon blue"><Plus size={18} /></span><span><strong>Tạo hồ sơ tuyển sinh</strong><small>Tiếp nhận nguyện vọng mới</small></span><ArrowRight size={16} /></Link>
          <Link className="quick-action" href="/support"><span className="quick-icon green"><CircleHelp size={18} /></span><span><strong>Gửi yêu cầu hỗ trợ</strong><small>Theo dõi yêu cầu của bạn</small></span><ArrowRight size={16} /></Link>
          <Link className="quick-action" href="/study-planner"><span className="quick-icon blue"><CalendarCheck2 size={18} /></span><span><strong>Kế hoạch học tập</strong><small>Quản lý deadline & lịch thi</small></span><ArrowRight size={16} /></Link>
          <Link className="quick-action" href="/profiles"><span className="quick-icon violet"><UsersRound size={18} /></span><span><strong>Tra cứu hồ sơ</strong><small>Thông tin người học</small></span><ArrowRight size={16} /></Link>
        </div>
      </section>
      {/* Widget Deadline & Lịch thi sắp tới */}
      <section className="study-schedule-widget">
        <div className="study-schedule-header">
          <div className="study-schedule-title">
            <span className="schedule-badge"><CalendarCheck2 size={15} /> TIẾN ĐỘ HỌC TẬP</span>
            <h3>Deadline & Lịch thi sắp tới</h3>
            <p>Tự động nhắc nhở và đồng bộ với Trợ lý AI lập lịch ôn tập</p>
          </div>
          <div className="study-schedule-actions">
            <Link href="/study-planner" className="button button-secondary button-small">Xem tất cả</Link>
            <Link href="/assistant" className="button button-primary button-small"><Bot size={15} /> Nhờ AI lập lịch</Link>
          </div>
        </div>
        <div className="study-task-cards">
          {(studySummary?.tasks ?? []).filter((t: any) => t.status !== "completed").slice(0, 3).length ? (
            (studySummary?.tasks ?? []).filter((t: any) => t.status !== "completed").slice(0, 3).map((task: any) => {
              const diff = new Date(task.due_date).getTime() - new Date().getTime();
              const days = Math.ceil(diff / (1000 * 60 * 60 * 24));
              const daysLabel = days < 0 ? `Quá hạn ${Math.abs(days)} ngày` : days === 0 ? "Hôm nay" : days === 1 ? "Ngày mai" : `Còn ${days} ngày`;
              const isUrgent = days <= 3;
              return (
                <div key={task.id} className="study-task-mini-card">
                  <div className="mini-card-top">
                    <span className={`task-badge ${task.task_type}`}>{task.task_type === "exam" ? "Lịch thi" : "Deadline"}</span>
                    <span className={`mini-card-countdown ${isUrgent ? "urgent" : ""}`}>{daysLabel}</span>
                  </div>
                  <h4>{task.title}</h4>
                  <div className="mini-card-foot">
                    <span>{task.course_name}</span>
                    <time>{new Date(task.due_date).toLocaleDateString("vi-VN", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" })}</time>
                  </div>
                </div>
              );
            })
          ) : (
            <div className="study-task-empty">
              <Clock size={16} />
              <span>Hiện không có deadline hay lịch thi nào cận kề. Hãy mở <Link href="/study-planner">Kế hoạch học tập</Link> để thêm mới!</span>
            </div>
          )}
        </div>
      </section>
      <section className="ai-banner"><div className="ai-banner-art"><div className="ai-orb"><Bot size={28} /></div><span className="sparkle s1">✦</span><span className="sparkle s2">✧</span><span className="orbit orbit-one" /><span className="orbit orbit-two" /></div><div className="ai-banner-copy"><div className="ai-label"><Sparkles size={14} /> STUDY AI ASSISTANT</div><h2>Trợ lý đại học của bạn,<br className="desktop-break" /> luôn sẵn sàng hỗ trợ.</h2><p>Tìm hiểu ngành đào tạo, quy trình tuyển sinh và thủ tục sinh viên từ dữ liệu tri thức của Study.</p><Link className="button button-light" href="/assistant">Bắt đầu trò chuyện <ArrowRight size={16} /></Link></div><div className="ai-banner-chips"><span>✦ Tư vấn tuyển sinh</span><span>⌕ Tra cứu hồ sơ</span><span>◌ Hỗ trợ 24/7*</span><small>* Demo: phản hồi phụ thuộc cấu hình LLM</small></div></section>
      <div className="dashboard-footnote">Số liệu biến động theo dữ liệu lưu trong hệ thống. Biểu đồ tuyển sinh sử dụng chuỗi mẫu minh họa.</div>
    </>}
  </div>;
}

function StatCard({ label, value, sub, icon: Icon, color, trend, up }: { label: string; value: number; sub: string; icon: typeof UsersRound; color: string; trend: string; up?: boolean }) {
  return <article className="stat-card"><div className="stat-card-top"><span>{label}</span><span className={`stat-icon ${color}`}><Icon size={18} /></span></div><div className="stat-value">{value.toLocaleString("vi-VN")}</div><div className="stat-footer"><span>{sub}</span><span className={`stat-trend ${up ? "positive" : ""}`}>{up ? <ArrowUpRight size={13} /> : null}{trend}</span></div></article>;
}

function AdmissionsChart({ data }: { data: DashboardData["admissions_by_month"] }) {
  if (!data.length) return <div className="chart-empty">Chưa có dữ liệu.</div>;
  const max = Math.max(...data.map(item => item.applications), 1);
  const points = data.map((item, index) => ({ x: 42 + index * 49, y: 160 - (item.applications / max) * 125, ...item }));
  const line = points.map(point => `${point.x},${point.y}`).join(" ");
  return <div className="line-chart-wrap"><div className="chart-legend"><span><i /> Hồ sơ tiếp nhận</span><small>Tổng theo tháng · Dữ liệu minh họa</small></div><svg viewBox="0 0 610 205" role="img" aria-label="Biểu đồ hồ sơ tuyển sinh theo tháng" className="line-chart"><defs><linearGradient id="line-fill" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stopColor="#66aef4" stopOpacity=".22" /><stop offset="1" stopColor="#66aef4" stopOpacity="0" /></linearGradient></defs>{[35, 75, 115, 155].map(y => <line key={y} x1="30" x2="590" y1={y} y2={y} stroke="#edf1f5" strokeDasharray="4 5" />)}<polygon points={`42,160 ${line} 581,160`} fill="url(#line-fill)"/><polyline points={line} fill="none" stroke="#358bd9" strokeWidth="3" strokeLinejoin="round" strokeLinecap="round"/>{points.map(point => <g key={point.month}><circle cx={point.x} cy={point.y} r="3.5" fill="#fff" stroke="#358bd9" strokeWidth="2"/><text x={point.x} y="188" textAnchor="middle" fill="#8995a4" fontSize="10">{point.month}</text></g>)}</svg></div>;
}

const chartColors = ["#398fdd", "#80c7aa", "#8c96e8", "#f0bd76", "#7cc4d2", "#d8dfe8"];
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
