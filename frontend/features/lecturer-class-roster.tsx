"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";
import { ErrorNotice, Loading, PageTitle } from "@/components/ui";

type StudentRow = { student_id: string; student_number: string; full_name: string; email: string; class_name: string; status: string };
type Roster = { offering: { id: string; course_code: string; course_name: string; section: string; lecturer_name: string }; items: StudentRow[]; count: number; page: number; page_size: number };

export function LecturerClassRoster() {
  const { offeringId } = useParams<{ offeringId: string }>();
  const [roster, setRoster] = useState<Roster | null>(null); const [query, setQuery] = useState("");
  const [page, setPage] = useState(1); const [studentNumber, setStudentNumber] = useState("");
  const [candidate, setCandidate] = useState<StudentRow | null>(null); const [error, setError] = useState("");
  const [busy, setBusy] = useState(false); const pageSize = 20;
  const load = useCallback(async () => {
    setBusy(true); setError("");
    try { setRoster(await api<Roster>(`/lecturer/classes/${offeringId}/students?q=${encodeURIComponent(query)}&page=${page}&page_size=${pageSize}`)); }
    catch (cause) { setError(cause instanceof Error ? cause.message : "Không tải được danh sách sinh viên."); }
    finally { setBusy(false); }
  }, [offeringId, query, page]);
  useEffect(() => { void load(); }, [load]);
  async function lookup() {
    setCandidate(null); setError("");
    try { setCandidate(await api<StudentRow>(`/lecturer/classes/${offeringId}/students/lookup?student_number=${encodeURIComponent(studentNumber.trim())}`)); }
    catch (cause) { setError(cause instanceof Error ? cause.message : "Không tìm thấy sinh viên."); }
  }
  async function addStudent() {
    if (!candidate) return;
    setBusy(true); setError("");
    try { await api(`/lecturer/classes/${offeringId}/students`, { method: "POST", body: JSON.stringify({ student_number: candidate.student_number }) }); setCandidate(null); setStudentNumber(""); if (page === 1) await load(); else setPage(1); }
    catch (cause) { setError(cause instanceof Error ? cause.message : "Không thêm được sinh viên."); }
    finally { setBusy(false); }
  }
  const pages = Math.max(1, Math.ceil((roster?.count ?? 0) / pageSize));
  return <div className="attendance-page"><PageTitle eyebrow="GIẢNG DẠY · LỚP HỌC PHẦN" title="Danh sách sinh viên" description={roster ? `${roster.offering.course_name} · ${roster.offering.course_code}-${roster.offering.section} · ${roster.offering.lecturer_name}` : "Danh sách theo lớp được phân công."} />{error && <ErrorNotice message={error} />}
    <section className="roster-toolbar"><label>Tìm mã sinh viên hoặc họ tên<input value={query} onChange={event => { setQuery(event.target.value); setPage(1); }} placeholder="Nhập mã hoặc tên" /></label><div className="roster-add"><label>Thêm sinh viên bằng mã<input value={studentNumber} onChange={event => setStudentNumber(event.target.value)} placeholder="Mã sinh viên" /></label><button className="button button-secondary" disabled={!studentNumber.trim()} onClick={() => void lookup()}>Tra cứu</button></div></section>
    {candidate && <section className="roster-candidate"><div><strong>{candidate.full_name}</strong><span>{candidate.student_number} · {candidate.email} · {candidate.class_name || "Chưa có lớp hành chính"}</span></div><button className="button button-primary" disabled={busy} onClick={() => void addStudent()}>Xác nhận thêm vào lớp</button><button className="button button-ghost" onClick={() => setCandidate(null)}>Hủy</button></section>}
    {busy && !roster ? <Loading label="Đang tải danh sách…" /> : <><div className="table-panel responsive-table"><table><thead><tr><th>STT</th><th>Mã sinh viên</th><th>Họ và tên</th><th>Email</th><th>Lớp hành chính</th><th>Trạng thái</th></tr></thead><tbody>{roster?.items.map((row, index) => <tr key={row.student_id}><td>{(page - 1) * pageSize + index + 1}</td><td>{row.student_number}</td><td>{row.full_name}</td><td>{row.email}</td><td>{row.class_name || "—"}</td><td>{row.status}</td></tr>)}</tbody></table>{!roster?.items.length && <p className="attendance-empty">Không có sinh viên trong lớp này.</p>}</div><div className="roster-pagination"><span>{roster?.count ?? 0} sinh viên · Trang {page}/{pages}</span><button className="button button-ghost" disabled={page <= 1 || busy} onClick={() => setPage(value => value - 1)}>Trang trước</button><button className="button button-ghost" disabled={page >= pages || busy} onClick={() => setPage(value => value + 1)}>Trang sau</button></div></>}
  </div>;
}
