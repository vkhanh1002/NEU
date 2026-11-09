"use client";

import { useCallback, useEffect, useState } from "react";
import { api } from "@/lib/api";
import { ErrorNotice, Loading, PageTitle, StatusBadge } from "@/components/ui";

type ClassItem = { id: string; course_code: string; course_name: string; section: string; semester: string };
type Score = number | string | null;
type GradeRow = { student_id: string; student_number: string; full_name: string; class_name: string; attendance_score: Score; midterm_score: Score; final_score: Score; total_score: Score; letter_grade: string };
type GradeAudit = { id: string; student_number: string; previous_values: Record<string, unknown>; new_values: Record<string, unknown>; created_at: string };
const scoreFields = ["attendance_score", "midterm_score", "final_score", "total_score"] as const;

export function LecturerGrades() {
  const [classes, setClasses] = useState<ClassItem[]>([]); const [offeringId, setOfferingId] = useState(""); const [offering, setOffering] = useState<{ course_code: string; course_name: string; section: string } | null>(null);
  const [rows, setRows] = useState<GradeRow[]>([]); const [audit, setAudit] = useState<GradeAudit[]>([]); const [error, setError] = useState(""); const [success, setSuccess] = useState(""); const [busyId, setBusyId] = useState(""); const [loading, setLoading] = useState(true);
  const loadRows = useCallback(async (id: string) => {
    if (!id) { setRows([]); setOffering(null); setAudit([]); return; }
    const [grades, history] = await Promise.all([
      api<{ offering: NonNullable<typeof offering>; items: GradeRow[] }>(`/lecturer/classes/${id}/grades`),
      api<{ items: GradeAudit[] }>(`/lecturer/classes/${id}/grades/audit`),
    ]);
    setOffering(grades.offering); setRows(grades.items); setAudit(history.items);
  }, []);
  useEffect(() => {
    let live = true;
    api<{ items: ClassItem[] }>("/lecturer/classes").then(data => {
      if (!live) return;
      setClasses(data.items);
      const requested = new URLSearchParams(window.location.search).get("offering");
      setOfferingId(data.items.find(item => item.id === requested)?.id ?? data.items[0]?.id ?? "");
    }).catch(reason => setError(reason instanceof Error ? reason.message : "Không tải được lớp học phần.")).finally(() => { if (live) setLoading(false); });
    return () => { live = false; };
  }, []);
  useEffect(() => { if (offeringId) void loadRows(offeringId).catch(reason => setError(reason instanceof Error ? reason.message : "Không tải được bảng điểm.")); }, [loadRows, offeringId]);
  function edit(studentId: string, field: keyof GradeRow, value: string) { setRows(current => current.map(row => row.student_id === studentId ? { ...row, [field]: value } as GradeRow : row)); setSuccess(""); }
  async function save(row: GradeRow) {
    setBusyId(row.student_id); setError(""); setSuccess("");
    const payload: Record<string, number | string | null> = {};
    for (const field of scoreFields) payload[field] = row[field] === "" || row[field] === null ? null : Number(row[field]);
    payload.letter_grade = row.letter_grade;
    try { await api(`/lecturer/classes/${offeringId}/grades/${row.student_id}`, { method: "PATCH", body: JSON.stringify(payload) }); await loadRows(offeringId); setSuccess(`Đã lưu điểm của ${row.full_name} và ghi lịch sử cập nhật.`); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Không lưu được điểm."); }
    finally { setBusyId(""); }
  }
  return <div className="attendance-page lecturer-grades-page"><PageTitle eyebrow="GIẢNG DẠY" title="Kết quả học tập" description="Cập nhật các cột điểm hiện có cho lớp được phân công. Mỗi lần lưu tạo lịch sử trước/sau." />{error && <ErrorNotice message={error} />}{success && <p className="attendance-note" role="status">{success}</p>}
    <section className="attendance-toolbar"><label>Lớp học phần<select value={offeringId} onChange={event => setOfferingId(event.target.value)}>{classes.map(item => <option key={item.id} value={item.id}>{item.course_code} · {item.section} — {item.course_name} ({item.semester})</option>)}</select></label></section>
    {loading ? <Loading /> : offering && <><div className="lecturer-grade-heading"><h2>{offering.course_code} · {offering.course_name} · Lớp {offering.section}</h2><StatusBadge>{rows.length} sinh viên</StatusBadge></div><div className="attendance-grade-table-wrap"><table className="attendance-grade-table"><thead><tr><th>Sinh viên</th><th>Điểm chuyên cần</th><th>Giữa kỳ</th><th>Cuối kỳ</th><th>Tổng kết</th><th>Điểm chữ</th><th></th></tr></thead><tbody>{rows.map(row => <tr key={row.student_id}><td><strong>{row.full_name}</strong><small>{row.student_number} · {row.class_name || "Chưa cập nhật lớp"}</small></td>{scoreFields.map(field => <td key={field}><input aria-label={`${field} của ${row.student_number}`} type="number" min="0" max="10" step="0.1" value={row[field] ?? ""} onChange={event => edit(row.student_id, field, event.target.value)} /></td>)}<td><select aria-label={`Điểm chữ của ${row.student_number}`} value={row.letter_grade} onChange={event => edit(row.student_id, "letter_grade", event.target.value)}><option value="">—</option>{["A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "F"].map(value => <option key={value}>{value}</option>)}</select></td><td><button className="button button-primary" disabled={busyId === row.student_id} onClick={() => void save(row)}>{busyId === row.student_id ? "Đang lưu…" : "Lưu"}</button></td></tr>)}</tbody></table>{!rows.length && <p className="attendance-empty">Lớp học phần chưa có sinh viên.</p>}</div><section className="attendance-admin-audit"><h2>Lịch sử cập nhật điểm</h2>{audit.map(item => <article key={item.id}><time>{new Date(item.created_at).toLocaleString("vi-VN")}</time><strong>{item.student_number}</strong><span>Trước: {summarize(item.previous_values)}</span><span>Sau: {summarize(item.new_values)}</span></article>)}{!audit.length && <p className="attendance-note">Chưa có lần cập nhật điểm nào.</p>}</section></>}
  </div>;
}

function summarize(values: Record<string, unknown>) { return `CC ${values.attendance_score ?? "—"} · GK ${values.midterm_score ?? "—"} · CK ${values.final_score ?? "—"} · Tổng ${values.total_score ?? "—"} · ${values.letter_grade || "—"}`; }
