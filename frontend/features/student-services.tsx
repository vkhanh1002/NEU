"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";
import { Award, BookOpen, CalendarDays, ClipboardList, Clock3, RefreshCw, Wallet } from "lucide-react";
import { EmptyState, ErrorNotice, Loading, PageTitle, StatusBadge } from "@/components/ui";
import { api } from "@/lib/api";

type ServiceKey = "schedule" | "exams" | "results" | "conduct" | "finance" | "assignments";
type Row = Record<string, unknown>;
type Semester = { id: string; code: string; name: string; academic_year: string; is_current: boolean };
const serviceMeta: Record<ServiceKey, { title: string; description: string; eyebrow: string; icon: typeof BookOpen }> = {
  schedule: { title: "Thời khóa biểu", description: "Lịch học theo học kỳ của tài khoản sinh viên.", eyebrow: "HỌC TẬP", icon: CalendarDays },
  exams: { title: "Lịch thi", description: "Theo dõi các kỳ thi sắp tới và lịch thi đã diễn ra.", eyebrow: "HỌC TẬP", icon: Clock3 },
  results: { title: "Kết quả học tập", description: "Bảng điểm, GPA và số tín chỉ tích lũy.", eyebrow: "HỌC TẬP", icon: BookOpen },
  conduct: { title: "Kết quả rèn luyện", description: "Lịch sử đánh giá rèn luyện theo học kỳ.", eyebrow: "HỌC TẬP", icon: Award },
  finance: { title: "Tài chính sinh viên", description: "Khoản thu, số dư và lịch sử giao dịch ghi nhận.", eyebrow: "DỊCH VỤ SINH VIÊN", icon: Wallet },
  assignments: { title: "Bài tập và hạn nộp", description: "Theo dõi tiến độ, nội dung và thời hạn của bài tập.", eyebrow: "HỌC TẬP", icon: ClipboardList },
};

export function StudentServicesPage({ service }: { service: ServiceKey }) {
  const meta = serviceMeta[service];
  const [payload, setPayload] = useState<Row>({});
  const [semesters, setSemesters] = useState<Semester[]>([]);
  const [semesterId, setSemesterId] = useState("");
  const [scheduleView, setScheduleView] = useState<"week" | "today" | "list">("week");
  const [status, setStatus] = useState("");
  const [submissions, setSubmissions] = useState<Record<string, string>>({});
  const [busyId, setBusyId] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const load = useCallback(async () => {
    setLoading(true); setError(""); setMessage("");
    try {
      let path = `/student/${service}`;
      const params = new URLSearchParams();
      if (semesterId === "all") params.set("semester_id", "all");
      else if (semesterId && semesterId !== "current" && ["schedule", "exams", "results"].includes(service)) params.set("semester_id", semesterId);
      if (status && service === "assignments") params.set("status", status);
      if (params.size) path += `?${params.toString()}`;
      const data = await api<Row>(path);
      setPayload(data);
      if (service !== "conduct" && !semesters.length) {
        const list = await api<Semester[]>("/student/semesters");
        setSemesters(list);
        const current = list.find(item => item.is_current);
        if (!semesterId && current && ["schedule", "exams", "results"].includes(service)) setSemesterId(current.id);
      }
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Không tải được dữ liệu."); }
    finally { setLoading(false); }
  }, [service, semesterId, status, semesters.length]);
  useEffect(() => { void load(); }, [load]);

  async function submit(assignmentId: string, event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const content = (submissions[assignmentId] ?? "").trim();
    if (!content) { setError("Nhập nội dung bài nộp trước khi gửi."); return; }
    setBusyId(assignmentId); setError(""); setMessage("");
    try {
      await api(`/student/assignments/${assignmentId}/submit`, { method: "POST", body: JSON.stringify({ content }) });
      setMessage("Đã ghi nhận bài nộp.");
      await load();
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Không gửi được bài nộp."); }
    finally { setBusyId(""); }
  }

  const Icon = meta.icon;
  const items = records(payload.items);
  const examRows: Row[] = [
    ...records(payload.upcoming).map(row => ({ ...row, _state: "Sắp tới" })),
    ...records(payload.past).map(row => ({ ...row, _state: "Đã diễn ra" })),
  ];
  return <div className="module-page student-service-page">
    <PageTitle eyebrow={meta.eyebrow} title={meta.title} description={meta.description} action={<button className="button button-secondary" onClick={() => void load()}><RefreshCw size={15} /> Tải lại</button>} />
    {service === "schedule" && <div className="module-toolbar student-toolbar"><div className="student-view-switch" role="tablist" aria-label="Cách xem thời khóa biểu"><button className={scheduleView === "week" ? "active" : ""} onClick={() => setScheduleView("week")}>Tuần</button><button className={scheduleView === "today" ? "active" : ""} onClick={() => setScheduleView("today")}>Hôm nay</button><button className={scheduleView === "list" ? "active" : ""} onClick={() => setScheduleView("list")}>Danh sách</button></div><label className="student-select-label">Học kỳ<select value={semesterId || "current"} onChange={event => setSemesterId(event.target.value)}><option value="current">Học kỳ hiện tại</option><option value="all">Tất cả học kỳ</option>{semesters.map(term => <option key={term.id} value={term.id}>{term.name}</option>)}</select></label></div>}
    {(service === "exams" || service === "results") && <div className="module-toolbar student-toolbar"><label className="student-select-label">Học kỳ<select value={semesterId || "current"} onChange={event => setSemesterId(event.target.value)}><option value="current">Học kỳ hiện tại</option><option value="all">Tất cả học kỳ</option>{semesters.map(term => <option key={term.id} value={term.id}>{term.name}</option>)}</select></label></div>}
    {error && <ErrorNotice message={error} />}{message && <div className="success-notice" role="status">{message}</div>}
    {loading ? <Loading label={`Đang tải ${meta.title.toLowerCase()}…`} /> : <>
      {service === "schedule" && <ScheduleContent items={items} scheduleView={scheduleView} />}
      {service === "exams" && <>{examRows.length ? <div className="student-data-table"><table><thead><tr><th>Trạng thái</th><th>Học phần</th><th>Ngày giờ</th><th>Phòng</th><th>Hình thức</th><th>Thời lượng</th></tr></thead><tbody>{examRows.map(row => <tr key={text(row.exam_id)}><td><StatusBadge>{text(row._state)}</StatusBadge></td><td><strong>{text(row.course_name)}</strong><small>{text(row.course_code)}</small></td><td>{formatDate(row.starts_at)}</td><td>{text(row.room)}</td><td>{text(row.exam_type)}</td><td>{text(row.duration_minutes)} phút</td></tr>)}</tbody></table></div> : <EmptyState icon={<Clock3 size={22} />} title="Chưa có lịch thi" description="Lịch thi sẽ được hiển thị sau khi học phần được cập nhật." />}</>}
      {service === "results" && <><div className="student-stat-grid"><Metric label="GPA" value={payload.gpa == null ? "—" : Number(payload.gpa).toFixed(2)} /><Metric label="Tín chỉ tích lũy" value={String(payload.credits_earned ?? 0)} /><Metric label="Học phần chưa đạt" value={String(records(payload.failed_courses).length)} /></div>{items.length ? <div className="student-data-table"><table><thead><tr><th>Học phần</th><th>Học kỳ</th><th>Chuyên cần</th><th>Giữa kỳ</th><th>Cuối kỳ</th><th>Tổng kết</th><th>Điểm chữ</th><th>Kết quả</th></tr></thead><tbody>{items.map(row => <tr key={text(row.id)}><td><strong>{text(row.course_name)}</strong><small>{text(row.course_code)} · {text(row.credits)} tín chỉ</small></td><td>{text(row.semester)}</td><td>{text(row.attendance_score)}</td><td>{text(row.midterm_score)}</td><td>{text(row.final_score)}</td><td>{text(row.total_score)}</td><td>{text(row.letter_grade)}</td><td><StatusBadge>{text(row.status)}</StatusBadge></td></tr>)}</tbody></table></div> : <EmptyState icon={<BookOpen size={22} />} title="Chưa có kết quả học tập" description="Kết quả sẽ xuất hiện sau khi điểm học phần được công bố." />}</>}
      {service === "conduct" && <>{items.length ? <div className="student-data-table"><table><thead><tr><th>Học kỳ</th><th>Điểm</th><th>Xếp loại</th><th>Trạng thái</th><th>Ngày đánh giá</th><th>Nhận xét</th></tr></thead><tbody>{items.map(row => <tr key={text(row.id)}><td>{text(row.semester)}</td><td><strong>{text(row.score)}/100</strong></td><td>{text(row.rating)}</td><td><StatusBadge>{text(row.status)}</StatusBadge></td><td>{formatDate(row.evaluated_at)}</td><td>{text(row.comment)}</td></tr>)}</tbody></table></div> : <EmptyState icon={<Award size={22} />} title="Chưa có kết quả rèn luyện" description="Lịch sử đánh giá sẽ hiển thị tại đây." />}</>}
      {service === "finance" && <><div className="student-stat-grid"><Metric label="Tổng khoản thu" value={money(payload.total_due)} /><Metric label="Đã thanh toán" value={money(payload.total_paid)} /><Metric label="Còn phải nộp" value={money(payload.total_remaining)} /></div>{items.length ? <div className="student-data-table"><table><thead><tr><th>Khoản thu</th><th>Học kỳ</th><th>Phải nộp</th><th>Đã nộp</th><th>Còn lại</th><th>Hạn</th><th>Trạng thái</th></tr></thead><tbody>{items.map(row => <tr key={text(row.id)}><td><strong>{text(row.title)}</strong>{records(row.transactions).map(tx => <small key={text(tx.id)}>Giao dịch {text(tx.reference)} · {money(tx.amount)} · {formatDate(tx.paid_at)}</small>)}</td><td>{text(row.semester)}</td><td>{money(row.amount_due)}</td><td>{money(row.amount_paid)}</td><td>{money(row.remaining)}</td><td>{formatDate(row.due_date)}</td><td><StatusBadge>{text(row.status)}</StatusBadge></td></tr>)}</tbody></table></div> : <EmptyState icon={<Wallet size={22} />} title="Chưa có khoản thu" description="Các khoản phải nộp sẽ hiển thị khi được bộ phận tài chính cập nhật." />}</>}
      {service === "assignments" && <>{items.length ? <div className="student-assignment-list">{items.map(row => <article className="student-assignment-card" key={text(row.id)}><div className="student-assignment-head"><div><small>{text(row.course_code)} · {text(row.semester)}</small><h2>{text(row.title)}</h2></div><StatusBadge>{text(row.status)}</StatusBadge></div><p>{text(row.description)}</p><div className="student-assignment-deadline">Hạn nộp: <strong>{formatDate(row.deadline)}</strong>{row.score != null && <span>Điểm: {text(row.score)}</span>}</div>{!["Đã chấm"].includes(text(row.status)) && <form onSubmit={event => void submit(text(row.id), event)} className="student-submit-form"><textarea rows={3} maxLength={10000} value={submissions[text(row.id)] ?? text(row.content)} onChange={event => setSubmissions(current => ({ ...current, [text(row.id)]: event.target.value }))} placeholder="Nhập nội dung bài nộp…" /><button className="button button-primary" disabled={busyId === text(row.id)}>{busyId === text(row.id) ? "Đang gửi…" : "Nộp bài"}</button></form>}</article>)}</div> : <EmptyState icon={<ClipboardList size={22} />} title="Chưa có bài tập" description="Bài tập được giao ở các học phần sẽ hiển thị tại đây." />}</>}
    </>}
    <span className="student-service-page-icon"><Icon size={17} /></span>
  </div>;
}

function Metric({ label, value }: { label: string; value: string }) { return <article className="student-metric"><small>{label}</small><strong>{value}</strong></article>; }
function ScheduleContent({ items, scheduleView }: { items: Row[]; scheduleView: "week" | "today" | "list" }) {
  if (!items.length) return <EmptyState icon={<CalendarDays size={22} />} title="Chưa có lịch học" description="Không tìm thấy học phần trong học kỳ đã chọn." />;
  const days = ["", "Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ nhật"];
  const today = new Date().getDay() || 7;
  const todayDate = localDateISO();
  const visible = scheduleView === "today" ? items.filter(row => text(row.class_date) === todayDate) : items;
  return <><div className="student-next-class"><CalendarDays size={17} /><span><strong>Buổi học sắp tới</strong><small>{describeNextClass(items)}</small></span></div>{scheduleView === "week" ? <div className="student-week-grid">{days.slice(1).map((day, index) => { const weekday = index + 1; const courses = items.filter(row => Number(row.weekday) === weekday); return <section key={day}><h2>{day}</h2>{courses.length ? courses.map(row => <article key={text(row.offering_id)}><time>{formatDate(text(row.class_date))} · {text(row.study_shift)}</time><strong>{text(row.course_name)}</strong><small>{text(row.course_code)} · {text(row.section_code)} · {text(row.starts_at)}–{text(row.ends_at)}</small><small>{text(row.lecturer)} · {text(row.room)}</small><small>{text(row.delivery_mode)}{row.note ? ` · ${text(row.note)}` : ""}</small></article>) : <p>Không có buổi học</p>}</section>; })}</div> : scheduleView === "today" && !visible.length ? <EmptyState icon={<CalendarDays size={22} />} title="Hôm nay không có buổi học" description="Bạn có thể chuyển sang xem thời khóa biểu cả tuần." /> : <div className="student-data-table"><table><thead><tr><th>Thứ / ngày / ca</th><th>Học phần</th><th>Giờ</th><th>Giảng viên</th><th>Phòng / hình thức</th><th>Học kỳ / ghi chú</th></tr></thead><tbody>{visible.map(row => <tr key={text(row.offering_id)}><td>{text(row.weekday_label)}<small>{formatDate(text(row.class_date))} · {text(row.study_shift)}</small></td><td><strong>{text(row.course_name)}</strong><small>{text(row.course_code)} · {text(row.section_name)} · {text(row.section_code)}</small></td><td>{text(row.starts_at)}–{text(row.ends_at)}</td><td>{text(row.lecturer)}</td><td>{text(row.room)} · {text(row.delivery_mode)}</td><td>{text(row.semester_name)}<small>{text(row.academic_year)}{row.note ? ` · ${text(row.note)}` : ""}</small></td></tr>)}</tbody></table></div>}</>;
}
function describeNextClass(items: Row[]) {
  const today = localDateISO();
  const upcoming = items.filter(row => text(row.class_date) >= today).sort((a, b) => text(a.class_date).localeCompare(text(b.class_date)) || text(a.starts_at).localeCompare(text(b.starts_at)))[0];
  if (!upcoming) return "Chưa có buổi học sắp tới.";
  return `${text(upcoming.weekday_label)}, ${formatDate(text(upcoming.class_date))} · ${text(upcoming.course_name)} · ${text(upcoming.study_shift)} ${text(upcoming.starts_at)} · ${text(upcoming.room)}`;
}
function daysLabel(day: number) { return day === 7 ? "Chủ nhật" : `Thứ ${day + 1}`; }
function records(value: unknown): Row[] { return Array.isArray(value) ? value.filter((item): item is Row => typeof item === "object" && item !== null) : []; }
function text(value: unknown): string { return value === null || value === undefined || value === "" ? "—" : String(value); }
function localDateISO(value = new Date()): string { return `${value.getFullYear()}-${String(value.getMonth()+1).padStart(2,"0")}-${String(value.getDate()).padStart(2,"0")}`; }
function formatDate(value: unknown): string { if (!value) return "—"; const raw = String(value); const dateOnly = /^(\d{4})-(\d{2})-(\d{2})$/.exec(raw); const date = dateOnly ? new Date(Number(dateOnly[1]),Number(dateOnly[2])-1,Number(dateOnly[3])) : new Date(raw); return Number.isNaN(date.getTime()) ? raw : date.toLocaleString("vi-VN"); }
function money(value: unknown): string { return new Intl.NumberFormat("vi-VN", { style: "currency", currency: "VND", maximumFractionDigits: 0 }).format(Number(value) || 0); }
