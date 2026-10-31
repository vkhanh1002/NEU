"use client";

import { useEffect, useMemo, useState } from "react";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { useSearchParams } from "next/navigation";
import { ArrowRight, BookOpen, Check, FilePlus2, Search, X } from "lucide-react";
import { api, Major } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { DemoTag, EmptyState, ErrorNotice, Loading, PageTitle, StatusBadge } from "@/components/ui";

type Applicant = { id: string; email: string; full_name: string; phone: string; desired_major_id: string; major_name: string; admission_method: string; status: string; created_at: string; student_id: string | null };
const applicationSchema = z.object({ full_name: z.string().min(2, "Nhập họ và tên."), email: z.string().email("Email chưa đúng định dạng."), phone: z.string().min(8, "Nhập số điện thoại hợp lệ."), desired_major_id: z.string().min(1, "Chọn ngành đăng ký."), admission_method: z.string().min(1) });
type ApplicationValues = z.infer<typeof applicationSchema>;
const staffRoles = ["super_admin", "admission_staff"];

export function Admissions() {
  const params = useSearchParams();
  const { user } = useAuth();
  const isStaff = !!user && staffRoles.includes(user.role);
  const [majors, setMajors] = useState<Major[]>([]);
  const [applications, setApplications] = useState<Applicant[]>([]);
  const [loading, setLoading] = useState(true);
  const [busyId, setBusyId] = useState("");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [search, setSearch] = useState(params.get("search") ?? "");
  const [showForm, setShowForm] = useState(false);
  const [selectedMajor, setSelectedMajor] = useState("");
  const [tab, setTab] = useState<"majors" | "applications">(isStaff ? "applications" : "majors");
  async function load() {
    setLoading(true); setError("");
    try {
      const majorRows = await api<Major[]>("/majors"); setMajors(majorRows);
      if (isStaff) setApplications(await api<Applicant[]>("/admissions/applications"));
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Không thể tải dữ liệu."); }
    finally { setLoading(false); }
  }
  useEffect(() => { void load(); }, [isStaff]);
  useEffect(() => { if (isStaff) setTab("applications"); else setTab("majors"); }, [isStaff]);
  const visibleMajors = useMemo(() => majors.filter(row => `${row.code} ${row.name} ${row.faculty_name}`.toLowerCase().includes(search.toLowerCase())), [majors, search]);
  const visibleApplications = useMemo(() => applications.filter(row => `${row.full_name} ${row.email} ${row.major_name} ${row.status}`.toLowerCase().includes(search.toLowerCase())), [applications, search]);
  async function updateStatus(row: Applicant, status: string) {
    setBusyId(row.id); setError("");
    try { await api(`/admissions/applications/${row.id}/status`, { method: "PATCH", body: JSON.stringify({ status }) }); await load(); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Cập nhật chưa thành công."); }
    finally { setBusyId(""); }
  }
  async function promote(row: Applicant) {
    setBusyId(row.id); setError("");
    try { const created = await api<{ student_number: string }>(`/admissions/applications/${row.id}/promote`, { method: "POST" }); setMessage(`Đã chuyển hồ sơ thành sinh viên ${created.student_number}.`); await load(); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Chuyển hồ sơ chưa thành công."); }
    finally { setBusyId(""); }
  }
  return <div className="module-page">
    <PageTitle eyebrow="NGHIỆP VỤ · ADMISSIONS" title="Tuyển sinh" description="Quản lý ngành đào tạo, hồ sơ đăng ký và quá trình xét tuyển." action={<button className="button button-primary" onClick={() => { setSelectedMajor(""); setShowForm(true); }}><FilePlus2 size={16} /> Tạo hồ sơ đăng ký</button>} />
    <div className="module-notice"><BookOpen size={16} /><span>Ngành, học phí và chỉ tiêu trong môi trường này là dữ liệu minh họa, không phải thông tin tuyển sinh chính thức.</span><DemoTag /></div>
    <div className="module-toolbar"><div className="tab-switch"><button className={tab === "majors" ? "selected" : ""} onClick={() => setTab("majors")}>Ngành đào tạo <span>{majors.length || 10}</span></button>{isStaff && <button className={tab === "applications" ? "selected" : ""} onClick={() => setTab("applications")}>Hồ sơ xét tuyển <span>{applications.length}</span></button>}</div><div className="search-field"><Search size={16} /><input value={search} onChange={event => setSearch(event.target.value)} placeholder="Tìm ngành, thí sinh…" /></div></div>
    {message && <div className="success-notice"><Check size={16} />{message}<button onClick={() => setMessage("")} aria-label="Đóng"><X size={15} /></button></div>}
    {error && <ErrorNotice message={error} />}
    {loading ? <Loading /> : tab === "majors" ? <MajorTable rows={visibleMajors} onApply={majorId => { setSelectedMajor(majorId); setShowForm(true); }} /> : isStaff ? <ApplicationTable rows={visibleApplications} isBusy={busyId} onStatus={updateStatus} onPromote={promote} /> : <EmptyState title="Đăng nhập để xem hồ sơ" description="Danh sách hồ sơ xét tuyển chỉ hiển thị cho nhân viên được phân quyền." />}
    {showForm && <ApplicationDialog majors={majors} initialMajorId={selectedMajor} onClose={() => setShowForm(false)} onCreated={async code => { setShowForm(false); setMessage(`Đã tiếp nhận hồ sơ ${code}.`); if (isStaff) await load(); }} />}
  </div>;
}

function MajorTable({ rows, onApply }: { rows: Major[]; onApply: (majorId: string) => void }) {
  if (!rows.length) return <EmptyState icon={<Search size={22} />} title="Không tìm thấy ngành phù hợp" description="Thử thay đổi nội dung tìm kiếm." />;
  return <div className="major-card-grid">{rows.map(major => <article key={major.id} className="major-card"><div className="major-card-head"><div className="major-code">{major.code}</div><StatusBadge>{major.admission_status}</StatusBadge></div><h3>{major.name}</h3><div className="major-faculty">{major.faculty_name}</div><p>{major.description}</p><div className="major-details"><div><span>Thời gian</span><strong>{major.duration_years} năm</strong></div><div><span>Học phí / năm</span><strong>{major.tuition_per_year_vnd.toLocaleString("vi-VN")} ₫</strong></div><div><span>Chỉ tiêu</span><strong>{major.admission_quota} <small>demo</small></strong></div></div><div className="major-card-bottom"><DemoTag /><button className="icon-text-button" onClick={() => onApply(major.id)}>Đăng ký <ArrowRight size={15} /></button></div></article>)}</div>;
}

function ApplicationTable({ rows, isBusy, onStatus, onPromote }: { rows: Applicant[]; isBusy: string; onStatus: (row: Applicant, status: string) => void; onPromote: (row: Applicant) => void }) {
  if (!rows.length) return <EmptyState icon={<FilePlus2 size={22} />} title="Chưa có hồ sơ xét tuyển" description="Hồ sơ đăng ký mới sẽ xuất hiện tại đây." />;
  return <div className="table-panel"><div className="responsive-table"><table><thead><tr><th>Thí sinh</th><th>Ngành đăng ký</th><th>Phương thức</th><th>Ngày tiếp nhận</th><th>Trạng thái</th><th>Thao tác</th></tr></thead><tbody>{rows.map(row => <tr key={row.id}><td><div className="person-cell"><span className="avatar small-avatar">{row.full_name[0]}</span><span><strong>{row.full_name}</strong><small>{row.email}</small></span></div></td><td>{row.major_name}</td><td>{row.admission_method}</td><td>{new Date(row.created_at).toLocaleDateString("vi-VN")}</td><td><StatusBadge>{row.status}</StatusBadge></td><td><div className="row-actions">{row.status !== "Trúng tuyển" && <select aria-label={`Cập nhật ${row.full_name}`} disabled={isBusy === row.id} value={row.status} onChange={event => onStatus(row, event.target.value)}><option>Mới tiếp nhận</option><option>Đang xét duyệt</option><option>Cần bổ sung</option><option>Trúng tuyển</option><option>Không trúng tuyển</option></select>}{row.status === "Trúng tuyển" && <button className="mini-button" disabled={isBusy === row.id} onClick={() => onPromote(row)}>{row.student_id ? "Đã chuyển" : "Tạo hồ sơ SV"}</button>}</div></td></tr>)}</tbody></table></div></div>;
}

function ApplicationDialog({ majors, initialMajorId, onClose, onCreated }: { majors: Major[]; initialMajorId: string; onClose: () => void; onCreated: (code: string) => void }) {
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const { register, handleSubmit, setValue, formState: { errors } } = useForm<ApplicationValues>({ resolver: zodResolver(applicationSchema), defaultValues: { admission_method: "Học bạ (demo)", desired_major_id: initialMajorId } });
  useEffect(() => { if (initialMajorId) setValue("desired_major_id", initialMajorId); }, [initialMajorId, setValue]);
  const submit = async (values: ApplicationValues) => {
    setBusy(true); setError("");
    try { const row = await api<{ id: string }>("/admissions/applications", { method: "POST", body: JSON.stringify(values) }); onCreated(row.id.slice(0, 8).toUpperCase()); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Không thể tiếp nhận hồ sơ."); }
    finally { setBusy(false); }
  };
  return <div className="modal-backdrop" onClick={onClose}><section className="form-modal" role="dialog" aria-modal="true" onClick={event => event.stopPropagation()}><div className="modal-heading"><div><div className="eyebrow">TUYỂN SINH DEMO</div><h2>Tạo hồ sơ đăng ký</h2><p>Thông tin sẽ được lưu vào hệ thống dữ liệu demo.</p></div><button className="modal-close" onClick={onClose} aria-label="Đóng"><X size={18} /></button></div>
    <form className="form-stack" onSubmit={handleSubmit(submit)}><label>Họ và tên<input {...register("full_name")} placeholder="Nguyễn Văn A" />{errors.full_name && <small className="field-error">{errors.full_name.message}</small>}</label><div className="form-row"><label>Email<input type="email" {...register("email")} placeholder="ban@example.com" />{errors.email && <small className="field-error">{errors.email.message}</small>}</label><label>Số điện thoại<input {...register("phone")} placeholder="09xx xxx xxx" />{errors.phone && <small className="field-error">{errors.phone.message}</small>}</label></div><label>Ngành đăng ký<select id="desired_major_id" {...register("desired_major_id")} defaultValue=""><option value="" disabled>Chọn ngành đào tạo</option>{majors.map(major => <option key={major.id} value={major.id}>{major.name} · {major.code}</option>)}</select>{errors.desired_major_id && <small className="field-error">{errors.desired_major_id.message}</small>}</label><label>Phương thức xét tuyển<select {...register("admission_method")}><option>Học bạ (demo)</option><option>Điểm thi tốt nghiệp THPT (demo)</option><option>Xét tuyển kết hợp (demo)</option></select></label>
      {error && <div className="inline-error">{error}</div>}<div className="modal-actions"><button type="button" className="button button-ghost" onClick={onClose}>Hủy</button><button className="button button-primary" disabled={busy}>{busy ? "Đang gửi…" : "Gửi hồ sơ"}<ArrowRight size={15} /></button></div></form>
  </section></div>;
}
