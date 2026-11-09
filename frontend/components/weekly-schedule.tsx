"use client";

import { useMemo, useState } from "react";
import { ArrowLeft, ArrowRight, CalendarDays, Printer, TriangleAlert } from "lucide-react";

type RecordRow = Record<string, unknown>;
type ScheduleView = "week" | "today" | "list";
const dayNames = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ nhật"];
const cardColors = ["#176d9b", "#438767", "#287e83", "#526f91", "#6b7e66", "#8a6b49"];

export function WeeklySchedule({ items, onSelect, includeToday = true }: { items: unknown[]; onSelect?: (item: RecordRow) => void; includeToday?: boolean }) {
  const [weekOffset, setWeekOffset] = useState(0);
  const [view, setView] = useState<ScheduleView>("week");
  const rows = items as RecordRow[];
  const weekdays = useMemo(() => {
    const today = new Date();
    const monday = new Date(today.getFullYear(), today.getMonth(), today.getDate() - ((today.getDay() + 6) % 7) + weekOffset * 7);
    const count = view === "today" ? 1 : 7;
    const start = view === "today" ? today : monday;
    return Array.from({ length: count }, (_, index) => new Date(start.getFullYear(), start.getMonth(), start.getDate() + index));
  }, [weekOffset, view]);
  const occurrences = rows.flatMap(item => {
    const weekday = Number(item.weekday);
    const date = weekdays.find(day => day.getDay() === weekday % 7 && isoDate(day) >= text(item.semester_starts_on) && isoDate(day) <= text(item.semester_ends_on));
    return date ? [{ item, date }] : [];
  });
  const slots = [...new Set(occurrences.map(row => `${text(row.item.starts_at)}–${text(row.item.ends_at)}`))]
    .sort((a, b) => a.slice(0, 5).localeCompare(b.slice(0, 5)));
  const conflicts = useMemo(() => {
    const found = new Set<string>();
    for (const day of weekdays) {
      const sameDay = occurrences.filter(row => isoDate(row.date) === isoDate(day));
      for (let i = 0; i < sameDay.length; i++) for (let j = i + 1; j < sameDay.length; j++) {
        if (overlaps(text(sameDay[i].item.starts_at), text(sameDay[i].item.ends_at), text(sameDay[j].item.starts_at), text(sameDay[j].item.ends_at))) {
          found.add(text(sameDay[i].item.offering_id)); found.add(text(sameDay[j].item.offering_id));
        }
      }
    }
    return found;
  }, [rows, weekOffset, view]);
  const weekLabel = weekdays.length === 1 ? formatDay(weekdays[0]) : `${formatDay(weekdays[0])} – ${formatDay(weekdays[6])}`;

  function changeWeek(amount: number) {
    setView("week"); setWeekOffset(current => current + amount);
  }
  function currentWeek() { setWeekOffset(0); setView("week"); }

  return <section className="weekly-schedule">
    <div className="weekly-schedule-toolbar"><div className="weekly-schedule-view" role="tablist" aria-label="Cách xem thời khóa biểu"><button className={view === "week" ? "active" : ""} onClick={() => setView("week")}>Tuần</button>{includeToday && <button className={view === "today" ? "active" : ""} onClick={() => { setWeekOffset(0); setView("today"); }}>Hôm nay</button>}<button className={view === "list" ? "active" : ""} onClick={() => setView("list")}>Danh sách</button></div><div className="weekly-schedule-navigation"><button className="button button-secondary button-small" onClick={() => changeWeek(-1)} aria-label="Tuần trước"><ArrowLeft size={15} /> Trước</button><strong><CalendarDays size={16} />{weekLabel}</strong><button className="button button-secondary button-small" onClick={() => changeWeek(1)} aria-label="Tuần sau">Sau <ArrowRight size={15} /></button><button className="button button-ghost button-small" onClick={currentWeek}>Tuần này</button><button className="button button-ghost button-small print-schedule" onClick={() => window.print()} title="In hoặc lưu PDF"><Printer size={15} /> In</button></div></div>
    {conflicts.size > 0 && <div className="schedule-conflict-notice"><TriangleAlert size={17} /><span>Có {conflicts.size} lớp học phần bị trùng thời gian trong tuần đang xem. Kiểm tra thông tin chi tiết trước khi đến lớp.</span></div>}
    {!items.length || !occurrences.length ? <div className="schedule-empty"><CalendarDays size={22} /><strong>{items.length ? "Không có buổi học trong tuần này" : "Chưa có lịch học"}</strong><span>{items.length ? "Tuần đã chọn nằm ngoài thời gian hoạt động của các học phần." : "Các học phần đã đăng ký sẽ hiển thị tại đây."}</span></div> : view === "list" ? <div className="weekly-schedule-list">{occurrences.sort((a, b) => isoDate(a.date).localeCompare(isoDate(b.date)) || text(a.item.starts_at).localeCompare(text(b.item.starts_at))).map(({ item, date }) => <ScheduleCard key={`${text(item.offering_id)}-${isoDate(date)}`} item={item} date={date} onSelect={onSelect} conflict={conflicts.has(text(item.offering_id))} />)}</div> : <div className="weekly-schedule-scroll"><table className="weekly-schedule-table"><thead><tr><th>Giờ học</th>{weekdays.map((day, index) => <th key={isoDate(day)}><span>{view === "today" ? "Hôm nay" : dayNames[index]}</span><small>{dateShort(day)}</small></th>)}</tr></thead><tbody>{slots.map(slot => <tr key={slot}><th className="schedule-time-cell">{slot.split("–")[0]}<small>{slot.split("–")[1]}</small></th>{weekdays.map(day => { const dayRows = occurrences.filter(row => isoDate(row.date) === isoDate(day) && `${text(row.item.starts_at)}–${text(row.item.ends_at)}` === slot); return <td key={isoDate(day)}>{dayRows.map(({ item }) => <ScheduleCard key={text(item.offering_id)} item={item} date={day} onSelect={onSelect} conflict={conflicts.has(text(item.offering_id))} compact />)}</td>; })}</tr>)}</tbody></table></div>}
    <div className="weekly-schedule-legend"><span><i style={{ background: cardColors[0] }} />Màu sắc phân biệt các học phần</span><small>Giờ học theo cấu hình học phần. Đổi lịch đột xuất cần đối chiếu thông báo của đơn vị phụ trách.</small></div>
  </section>;
}

function ScheduleCard({ item, date, onSelect, conflict, compact = false }: { item: RecordRow; date: Date; onSelect?: (item: RecordRow) => void; conflict: boolean; compact?: boolean }) {
  const code = text(item.course_code); const index = [...code].reduce((sum, char) => sum + char.charCodeAt(0), 0) % cardColors.length;
  const content = <><span className="schedule-course-title">{text(item.course_name)}</span><span className="schedule-course-code">{code} · {text(item.section_code)}</span><span className="schedule-course-details">{text(item.study_shift)} · {text(item.room)}</span>{item.lecturer && <span className="schedule-course-details">{text(item.lecturer)}</span>}{conflict && <span className="schedule-course-conflict">Trùng lịch</span>}</>;
  const className = `schedule-course-card${compact ? " compact" : ""}${conflict ? " conflict" : ""}${onSelect ? " interactive" : ""}`;
  return onSelect ? <button className={className} style={{ "--schedule-accent": cardColors[index] } as React.CSSProperties} onClick={() => onSelect(item)} title={`${text(item.course_name)} · ${formatDay(date)}`}>{content}</button> : <article className={className} style={{ "--schedule-accent": cardColors[index] } as React.CSSProperties}>{content}</article>;
}

function overlaps(aStart: string, aEnd: string, bStart: string, bEnd: string) { return toMinutes(aStart) < toMinutes(bEnd) && toMinutes(bStart) < toMinutes(aEnd); }
function toMinutes(value: string) { const [hour, minute] = value.split(":").map(Number); return hour * 60 + minute; }
function text(value: unknown) { return value === undefined || value === null || value === "" ? "—" : String(value); }
function isoDate(value: Date) { return `${value.getFullYear()}-${String(value.getMonth() + 1).padStart(2, "0")}-${String(value.getDate()).padStart(2, "0")}`; }
function formatDay(value: Date) { return value.toLocaleDateString("vi-VN", { day: "numeric", month: "short", year: "numeric" }); }
function dateShort(value: Date) { return value.toLocaleDateString("vi-VN", { day: "2-digit", month: "2-digit" }); }
