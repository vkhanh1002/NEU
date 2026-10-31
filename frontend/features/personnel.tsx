"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { BriefcaseBusiness, GraduationCap, Plus, Search, UsersRound } from "lucide-react";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { EmptyState, ErrorNotice, Loading, PageTitle, StatusBadge } from "@/components/ui";

type Kind = "lecturer" | "employee";
type PersonnelRecord = {
  id: string; code: string; kind: Kind; full_name: string; email: string; phone: string; date_of_birth: string | null;
  gender: string; address: string; avatar_url: string; education_level: string; academic_rank: string; specialty: string;
  faculty_id: string | null; faculty_name: string | null; department: string; position: string; start_date: string | null;
  work_status: string; notes: string; is_demo: boolean;
};
type Faculty = { id: string; name: string };
type PersonnelDashboard = { lecturers: number; employees: number; total: number; active: number; inactive: number; by_status: { name: string; count: number }[]; by_unit: { name: string; count: number }[] };
const statuses = ["Đang công tác", "Tạm nghỉ", "Đã nghỉ việc"];

export function Personnel({ initialKind = "" }: { initialKind?: "" | Kind }) {
  const { user } = useAuth();
  const [rows, setRows] = useState<PersonnelRecord[]>([]); const [faculties, setFaculties] = useState<Faculty[]>([]);
  const [dashboard, setDashboard] = useState<PersonnelDashboard | null>(null); const [loading, setLoading] = useState(true); const [error, setError] = useState("");
  const [query, setQuery] = useState(""); const [status, setStatus] = useState(""); const [department, setDepartment] = useState("");
  const [selected, setSelected] = useState<PersonnelRecord | null>(null); const [createOpen, setCreateOpen] = useState(false);
  const pageTitle = initialKind === "lecturer" ? "Hồ sơ giảng viên" : initialKind === "employee" ? "Hồ sơ nhân viên" : "Tổng quan nhân sự";
  useEffect(() => {
    let live = true; const timer = setTimeout(() => {
      setLoading(true); const params = new URLSearchParams(); if (initialKind) params.set("kind", initialKind);
      if (query.trim()) params.set("q", query.trim()); if (status) params.set("status", status); if (department.trim()) params.set("department", department.trim());
      api<PersonnelRecord[]>(`/personnel${params.size ? `?${params}` : ""}`)
        .then(people => { if (live) { setRows(people); setError(""); } })
        .catch(reason => { if (live) setError(reason instanceof Error ? reason.message : "Không tải được hồ sơ nhân sự."); })
        .finally(() => { if (live) setLoading(false); });
    }, 200);
    return () => { live = false; clearTimeout(timer); };
  }, [initialKind, query, status, department]);
  useEffect(() => {
    let live = true;
    Promise.all([api<PersonnelDashboard>("/personnel/dashboard"), api<Faculty[]>("/faculties")])
      .then(([summary, facultyRows]) => { if (live) { setDashboard(summary); setFaculties(facultyRows); } })
      .catch(reason => { if (live) setError(reason instanceof Error ? reason.message : "Không tải được tổng quan nhân sự."); });
    return () => { live = false; };
  }, [user?.id]);
  const visibleRows = useMemo(() => rows, [rows]);
  function upsert(record: PersonnelRecord) {
    setRows(current => current.some(row => row.id === record.id) ? current.map(row => row.id === record.id ? record : row) : [...current, record].sort((a, b) => a.code.localeCompare(b.code)));
    setSelected(record); setCreateOpen(false);
    void api<PersonnelDashboard>("/personnel/dashboard").then(setDashboard).catch(() => {});
  }
  const staffKind = initialKind === "lecturer" ? "giảng viên" : "nhân viên";
  return <div className="module-page">
    <PageTitle eyebrow="QUẢN LÝ HỒ SƠ" title={pageTitle} description="Quản lý tập trung hồ sơ giảng viên và nhân viên theo đơn vị, chức vụ và trạng thái công tác." action={<button className="button button-primary" onClick={() => setCreateOpen(true)}><Plus size={17} /> Thêm {initialKind ? staffKind : "nhân sự"}</button>} />
    {error && <ErrorNotice message={error} />}
    {dashboard && <div className="personnel-stat-grid"><div className="personnel-stat-card"><span><UsersRound size={18} /> Tổng nhân sự</span><strong>{dashboard.total}</strong><small>{dashboard.active} đang công tác · {dashboard.inactive} nghỉ/tạm nghỉ</small></div><div className="personnel-stat-card"><span><GraduationCap size={19} /> Giảng viên</span><strong>{dashboard.lecturers}</strong><small>Hồ sơ học thuật và giảng dạy</small></div><div className="personnel-stat-card"><span><BriefcaseBusiness size={18} /> Nhân viên</span><strong>{dashboard.employees}</strong><small>Hồ sơ theo phòng ban và vị trí</small></div><div className="personnel-stat-card status-breakdown"><span>Tình trạng làm việc</span><div>{dashboard.by_status.map(item => <span key={item.name}><i className={item.name === "Đang công tác" ? "active" : "inactive"} />{item.name}<strong>{item.count}</strong></span>)}</div></div></div>}
    {initialKind === "" && dashboard && <section className="unit-chart-panel"><div className="section-heading"><div><h2>Phân bố theo đơn vị</h2><p>Số lượng giảng viên và nhân viên theo khoa/phòng ban</p></div></div><div className="unit-chart">{dashboard.by_unit.map(unit => <div className="unit-chart-row" key={unit.name}><span>{unit.name}</span><div><i style={{ width: `${Math.max(3, Math.round(unit.count * 100 / Math.max(...dashboard.by_unit.map(row => row.count), 1)))}%` }} /></div><strong>{unit.count}</strong></div>)}</div></section>}
    <div className="personnel-tabs"><a className={initialKind === "" ? "active" : ""} href="/personnel">Tổng quan</a><a className={initialKind === "lecturer" ? "active" : ""} href="/personnel/lecturers">Giảng viên</a><a className={initialKind === "employee" ? "active" : ""} href="/personnel/employees">Nhân viên</a></div>
    <div className="personnel-toolbar"><div className="toolbar-count">{initialKind ? `Danh sách ${staffKind}` : "Tất cả hồ sơ"} <strong>{visibleRows.length}</strong></div><label className="search-field"><Search size={17} /><input value={query} onChange={event => setQuery(event.target.value)} placeholder="Tên, mã, khoa, chuyên môn…" /></label><label><span className="sr-only">Lọc phòng ban</span><input value={department} onChange={event => setDepartment(event.target.value)} placeholder="Khoa / phòng ban" /></label><select aria-label="Lọc trạng thái công tác" value={status} onChange={event => setStatus(event.target.value)}><option value="">Mọi trạng thái</option>{statuses.map(value => <option key={value}>{value}</option>)}</select></div>
    {loading ? <Loading /> : visibleRows.length === 0 ? <EmptyState icon={<UsersRound size={24} />} title="Chưa có hồ sơ phù hợp" description="Thay đổi bộ lọc hoặc thêm hồ sơ nhân sự mới." action={<button className="button button-secondary" onClick={() => setCreateOpen(true)}>Thêm hồ sơ</button>} /> : <div className="table-panel"><div className="responsive-table"><table><thead><tr><th>Mã hồ sơ</th><th>Họ và tên</th><th>Đơn vị / chuyên môn</th><th>Chức vụ</th><th>Liên hệ</th><th>Trạng thái</th><th></th></tr></thead><tbody>{visibleRows.map(row => <tr key={row.id}><td><strong className="mono">{row.code}</strong><small className="personnel-kind">{row.kind === "lecturer" ? "Giảng viên" : "Nhân viên"}</small></td><td><div className="person-cell">{row.avatar_url ? <img className="personnel-avatar" src={row.avatar_url} alt="" /> : <span className="avatar small-avatar">{row.full_name.slice(0, 1)}</span>}<span><strong>{row.full_name}</strong><small>{row.email}</small></span></div></td><td>{row.faculty_name || row.department || "Chưa phân đơn vị"}<small className="personnel-kind">{row.specialty || row.education_level || ""}</small></td><td>{row.position || "—"}</td><td>{row.phone || "—"}</td><td><StatusBadge>{row.work_status}</StatusBadge></td><td><button className="mini-button" onClick={() => setSelected(row)}>Chi tiết</button></td></tr>)}</tbody></table></div></div>}
    {selected && <PersonnelDialog record={selected} faculties={faculties} onClose={() => setSelected(null)} onSaved={upsert} />}
    {createOpen && <PersonnelDialog kind={initialKind || "lecturer"} faculties={faculties} onClose={() => setCreateOpen(false)} onSaved={upsert} />}
  </div>;
}

const emptyRecord = (kind: Kind): PersonnelRecord => ({ id: "", code: "", kind, full_name: "", email: "", phone: "", date_of_birth: null, gender: "Chưa cập nhật", address: "", avatar_url: "", education_level: "", academic_rank: "", specialty: "", faculty_id: null, faculty_name: null, department: "", position: "", start_date: null, work_status: "Đang công tác", notes: "", is_demo: true });
function PersonnelDialog({ record, kind, faculties, onClose, onSaved }: { record?: PersonnelRecord; kind?: Kind; faculties: Faculty[]; onClose: () => void; onSaved: (row: PersonnelRecord) => void }) {
  const [editing, setEditing] = useState(!record); const [value, setValue] = useState<PersonnelRecord>(() => record ? { ...record } : emptyRecord(kind ?? "lecturer"));
  const [busy, setBusy] = useState(false); const [error, setError] = useState("");
  function change(field: string, next: string) { setValue(current => ({ ...current, [field]: next })); }
  async function save(event: React.FormEvent) {
    event.preventDefault(); setBusy(true); setError("");
    const payload = { ...value, date_of_birth: value.date_of_birth || null, start_date: value.start_date || null, faculty_id: value.faculty_id || null };
    try {
      const { id: _id, faculty_name: _facultyName, is_demo: _isDemo, ...personnelPayload } = payload;
      const body = record ? Object.fromEntries(Object.entries(personnelPayload).filter(([key]) => key !== "kind" && key !== "code")) : personnelPayload;
      const saved = await api<PersonnelRecord>(record ? `/personnel/${record.id}` : "/personnel", { method: record ? "PATCH" : "POST", body: JSON.stringify(body) });
      onSaved(saved);
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Không lưu được hồ sơ."); }
    finally { setBusy(false); }
  }
  const field = (label: string, key: keyof typeof value, type = "text") => <label>{label}<input type={type} value={(value[key] as string | null) ?? ""} readOnly={record && key === "code"} onChange={event => change(key, event.target.value)} /></label>;
  return <div className="modal-backdrop" onClick={onClose}><section className="personnel-modal" role="dialog" aria-modal="true" onClick={event => event.stopPropagation()}><div className="modal-heading"><div><div className="eyebrow">{value.kind === "lecturer" ? "HỒ SƠ GIẢNG VIÊN" : "HỒ SƠ NHÂN VIÊN"}</div><h2>{record ? editing ? "Chỉnh sửa hồ sơ" : value.full_name : "Thêm hồ sơ nhân sự"}</h2><p>{record ? value.code : "Thông tin được lưu trực tiếp qua API nhân sự."}</p></div><button className="modal-close" onClick={onClose}>×</button></div>
    {!editing && record ? <><div className="personnel-detail-grid">{[["Mã hồ sơ", value.code], ["Email", value.email], ["Điện thoại", value.phone], ["Ngày sinh", value.date_of_birth || "—"], ["Giới tính", value.gender], ["Địa chỉ", value.address], ["Trình độ", value.education_level], ["Học hàm / học vị", value.academic_rank], ["Chuyên môn", value.specialty], ["Khoa / phòng ban", value.faculty_name || value.department], ["Chức vụ", value.position], ["Ngày bắt đầu", value.start_date || "—"], ["Tình trạng", value.work_status]].map(([label, text]) => <div key={label}><span>{label}</span><strong>{text || "—"}</strong></div>)}</div><div className="modal-actions"><button className="button button-ghost" onClick={onClose}>Đóng</button><button className="button button-primary" onClick={() => setEditing(true)}>Chỉnh sửa</button></div></> : <form className="form-stack personnel-form" onSubmit={save}><div className="form-row">{!record && <label>Loại hồ sơ<select value={value.kind} onChange={event => change("kind", event.target.value)}><option value="lecturer">Giảng viên</option><option value="employee">Nhân viên</option></select></label>}{field("Mã hồ sơ", "code")}</div><div className="form-row">{field("Họ và tên", "full_name")}{field("Email", "email", "email")}</div><div className="form-row">{field("Số điện thoại", "phone")}{field("Ngày sinh", "date_of_birth", "date")}</div><div className="form-row"><label>Giới tính<select value={value.gender} onChange={event => change("gender", event.target.value)}>{["Chưa cập nhật", "Nữ", "Nam", "Khác"].map(v => <option key={v}>{v}</option>)}</select></label>{field("Ảnh đại diện (URL)", "avatar_url")}</div>{field("Địa chỉ", "address")}<div className="form-row">{field("Trình độ học vấn", "education_level")}{field("Học hàm / học vị", "academic_rank")}</div><div className="form-row">{field("Chuyên ngành", "specialty")}<label>Khoa<select value={value.faculty_id ?? ""} onChange={event => change("faculty_id", event.target.value)}><option value="">Chọn khoa (nếu có)</option>{faculties.map(faculty => <option key={faculty.id} value={faculty.id}>{faculty.name}</option>)}</select></label></div><div className="form-row">{field("Khoa / phòng ban", "department")}{field("Chức vụ", "position")}</div><div className="form-row">{field("Ngày bắt đầu công tác / tuyển dụng", "start_date", "date")}<label>Trạng thái làm việc<select value={value.work_status} onChange={event => change("work_status", event.target.value)}>{statuses.map(v => <option key={v}>{v}</option>)}</select></label></div><label>Thông tin bổ sung<textarea rows={3} value={value.notes} onChange={event => change("notes", event.target.value)} /></label>{error && <ErrorNotice message={error} />}<div className="modal-actions"><button type="button" className="button button-ghost" onClick={onClose}>Hủy</button><button className="button button-primary" disabled={busy}>{busy ? "Đang lưu…" : "Lưu hồ sơ"}</button></div></form>}</section></div>;
}
