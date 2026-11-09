"use client";

import { useEffect, useState } from "react";
import { CalendarDays, UsersRound } from "lucide-react";
import { api } from "@/lib/api";
import { ErrorNotice, Loading, PageTitle } from "@/components/ui";
import { WeeklySchedule } from "@/components/weekly-schedule";

type Meeting = { offering_id: string; course_code: string; course_name: string; section_name: string; section_code: string; lecturer: string; weekday_label: string; class_date: string; study_shift: string; starts_at: string; ends_at: string; room: string; semester_name: string; academic_year: string; delivery_mode: string; note: string };
type Schedule = { lecturer: { full_name: string; code: string }; items: Meeting[]; today: Meeting[]; next_class: Meeting | null; week_count: number; semesters: { id: string; name: string; academic_year: string; is_current: boolean }[]; courses: [string,string][]; sections: string[] };

export function LecturerSchedule() {
  const [data, setData] = useState<Schedule | null>(null);
  const [error, setError] = useState("");
  const [semester, setSemester] = useState("");
  const [academicYear, setAcademicYear] = useState("");
  const [course, setCourse] = useState("");
  const [section, setSection] = useState("");
  const [selected, setSelected] = useState<Meeting | null>(null);
  const [students, setStudents] = useState<{ student_number: string; full_name: string; class_name: string }[]>([]);
  const [busy, setBusy] = useState(false);
  async function load() {
    setBusy(true); setError("");
    try {
      const params = new URLSearchParams();
      if (semester) params.set("semester_id", semester);
      if (academicYear) params.set("academic_year", academicYear);
      if (course) params.set("course_code", course);
      if (section) params.set("section", section);
      const result = await api<Schedule>(`/lecturer/schedule${params.size ? `?${params}` : ""}`);
      setData(result);
      const requestedOffering = new URLSearchParams(window.location.search).get("offering") ?? "";
      if (requestedOffering) {
        const meeting = result.items.find(item => item.offering_id === requestedOffering);
        if (meeting) void openClass(meeting);
      }
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Không tải được thời khóa biểu giảng dạy."); }
    finally { setBusy(false); }
  }
  useEffect(() => { void load(); }, [semester, academicYear, course, section]);
  async function openClass(item: Meeting) {
    setSelected(item); setStudents([]);
    try { const response = await api<{ items: typeof students }>(`/lecturer/schedule/${item.offering_id}/students`); setStudents(response.items); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Không tải được danh sách lớp."); }
  }
  return <div className="lecturer-schedule-page"><PageTitle eyebrow="GIẢNG DẠY" title="Thời khóa biểu giảng dạy" description={data ? `${data.lecturer.full_name} · ${data.lecturer.code}` : "Các lớp học phần được phân công cho tài khoản của bạn."} />
    {error && <ErrorNotice message={error} />}
    <div className="lecturer-schedule-toolbar"><label>Học kỳ<select value={semester} onChange={e => setSemester(e.target.value)}><option value="">Học kỳ hiện tại</option><option value="all">Tất cả học kỳ</option>{data?.semesters.map(term => <option value={term.id} key={term.id}>{term.name}</option>)}</select></label><label>Năm học<select value={academicYear} onChange={e => setAcademicYear(e.target.value)}><option value="">Tất cả năm học</option>{Array.from(new Set(data?.semesters.map(term => term.academic_year) ?? [])).map(year => <option key={year}>{year}</option>)}</select></label><label>Môn học<select value={course} onChange={e => setCourse(e.target.value)}><option value="">Tất cả môn</option>{data?.courses.map(([code,name]) => <option value={code} key={code}>{code} · {name}</option>)}</select></label><label>Lớp học phần<select value={section} onChange={e => setSection(e.target.value)}><option value="">Tất cả lớp</option>{data?.sections.map(value => <option key={value}>{value}</option>)}</select></label></div>
    {busy && !data ? <Loading label="Đang tải lịch giảng dạy…" /> : <>
      <div className="lecturer-schedule-summary"><article><small>LỊCH HÔM NAY</small><strong>{data?.today.length ?? 0} buổi</strong><span>{data?.today[0] ? `${data.today[0].starts_at} · ${data.today[0].course_name}` : "Không có buổi dạy hôm nay"}</span></article><article><small>BUỔI TIẾP THEO</small><strong>{data?.next_class?.class_date ? dateLabel(data.next_class.class_date) : "Chưa có"}</strong><span>{data?.next_class ? `${data.next_class.course_name} · ${data.next_class.starts_at}` : "Không có lịch sắp tới"}</span></article><article><small>TRONG TUẦN</small><strong>{data?.week_count ?? 0} buổi</strong><span>Lịch theo các lớp được phân công</span></article></div>
      {data?.items.length ? <WeeklySchedule items={data.items} onSelect={item => void openClass(item as Meeting)} includeToday={false} /> : <div className="student-empty">Chưa có lớp học phần được phân công trong bộ lọc này.</div>}
    </>}
    {selected && <div className="modal-backdrop" onClick={() => setSelected(null)}><section className="lecturer-roster-modal" role="dialog" aria-modal="true" onClick={e => e.stopPropagation()}><header><div><small>{selected.section_code}</small><h2>{selected.course_name} · {selected.section_name}</h2><p>{selected.weekday_label}, {dateLabel(selected.class_date)} · {selected.study_shift}, {selected.starts_at}–{selected.ends_at} · {selected.room}</p><p>{selected.lecturer} · {selected.delivery_mode} · {selected.semester_name} · {selected.academic_year}</p>{selected.note && <p>{selected.note}</p>}</div><button onClick={() => setSelected(null)} aria-label="Đóng">×</button></header><h3><UsersRound size={16} /> Danh sách sinh viên ({students.length})</h3>{students.length ? <div className="lecturer-roster-list">{students.map(row => <div key={row.student_number}><strong>{row.full_name}</strong><span>{row.student_number} · {row.class_name || "Chưa xếp lớp"}</span></div>)}</div> : <p className="student-empty">Lớp chưa có sinh viên đăng ký.</p>}</section></div>}
  </div>;
}

function dateLabel(value: string) { return new Date(`${value}T12:00:00`).toLocaleDateString("vi-VN", { day: "2-digit", month: "2-digit", year: "numeric" }); }
