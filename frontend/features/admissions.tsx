"use client";

import { useEffect, useMemo, useState } from "react";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { useSearchParams } from "next/navigation";
import { ArrowRight, Check, FilePlus2, Search, X } from "lucide-react";
import { api, Major } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { EmptyState, ErrorNotice, Loading, PageTitle, StatusBadge } from "@/components/ui";

type Applicant = { id: string; email: string; full_name: string; phone: string; desired_major_id: string; major_name: string; admission_method: string; status: string; review_note: string; created_at: string; student_id: string | null };
const applicationSchema = z.object({ full_name: z.string().min(2, "Nhập họ và tên."), email: z.string().email("Email chưa đúng định dạng."), password: z.string().optional(), phone: z.string().min(8, "Nhập số điện thoại hợp lệ."), desired_major_id: z.string().min(1, "Chọn ngành đăng ký."), admission_method: z.string().min(1) });
type ApplicationValues = z.infer<typeof applicationSchema>;
const staffRoles = ["super_admin", "admission_staff"];

export function Admissions() {
  const params = useSearchParams();
  const { user } = useAuth();
  const isStaff = !!user && staffRoles.includes(user.role);
  const isApplicant = user?.role === "applicant";
  const [majors, setMajors] = useState<Major[]>([]);
  const [applications, setApplications] = useState<Applicant[]>([]);
  const [reviewNotes, setReviewNotes] = useState<Record<string, string>>({});
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
      else if (isApplicant) setApplications(await api<Applicant[]>("/admissions/applications/me"));
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Không thể tải dữ liệu."); }
    finally { setLoading(false); }
  }
  useEffect(() => { void load(); }, [isStaff, isApplicant]);
  useEffect(() => { if (isStaff) setTab("applications"); else setTab("majors"); }, [isStaff]);
  const visibleMajors = useMemo(() => majors.filter(row => `${row.code} ${row.name} ${row.faculty_name}`.toLowerCase().includes(search.toLowerCase())), [majors, search]);
  const visibleApplications = useMemo(() => applications.filter(row => `${row.full_name} ${row.email} ${row.major_name} ${row.status}`.toLowerCase().includes(search.toLowerCase())), [applications, search]);
  async function updateStatus(row: Applicant, status: string, note = reviewNotes[row.id] ?? row.review_note) {
    setBusyId(row.id); setError("");
    try { await api(`/admissions/applications/${row.id}/status`, { method: "PATCH", body: JSON.stringify({ status, note }) }); await load(); }
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
    <PageTitle eyebrow={isApplicant ? "TÀI KHOẢN THÍ SINH" : "TUYỂN SINH"} title={isApplicant ? "Hồ sơ của tôi" : "Tuyển sinh"} description={isApplicant ? "Theo dõi trạng thái và thông tin hồ sơ đã gửi." : "Tìm hiểu ngành học và theo dõi quá trình tiếp nhận hồ sơ."} action={(!user || (isApplicant && applications.length === 0)) ? <button className="button button-primary" onClick={() => { setSelectedMajor(""); setShowForm(true); }}><FilePlus2 size={16} /> Tạo hồ sơ đăng ký</button> : null} />
    {!isApplicant && <div className="module-toolbar"><div className="tab-switch"><button className={tab === "majors" ? "selected" : ""} onClick={() => setTab("majors")}>Ngành đào tạo <span>{majors.length}</span></button>{isStaff && <button className={tab === "applications" ? "selected" : ""} onClick={() => setTab("applications")}>Hồ sơ xét tuyển <span>{applications.length}</span></button>}</div><div className="search-field"><Search size={16} /><input value={search} onChange={event => setSearch(event.target.value)} placeholder="Tìm ngành, thí sinh…" /></div></div>}
    {message && <div className="success-notice"><Check size={16} />{message}<button onClick={() => setMessage("")} aria-label="Đóng"><X size={15} /></button></div>}
    {error && <ErrorNotice message={error} />}
    {loading ? <Loading /> : isApplicant ? <ApplicantApplications rows={applications} /> : tab === "majors" ? <MajorTable rows={visibleMajors} onApply={majorId => { setSelectedMajor(majorId); setShowForm(true); }} /> : isStaff ? <ApplicationTable rows={visibleApplications} isBusy={busyId} notes={reviewNotes} onNoteChange={(id, note) => setReviewNotes(current => ({ ...current, [id]: note }))} onStatus={updateStatus} onPromote={promote} /> : <EmptyState title="Đăng nhập để xem hồ sơ" description="Danh sách hồ sơ xét tuyển chỉ hiển thị cho nhân viên được phân quyền." />}
    {showForm && <ApplicationDialog majors={majors} initialMajorId={selectedMajor} onClose={() => setShowForm(false)} onCreated={async code => { setShowForm(false); setMessage(isApplicant ? `Đã tiếp nhận hồ sơ ${code}.` : `Đã tiếp nhận hồ sơ ${code}. Dùng email và mật khẩu vừa tạo để đăng nhập, theo dõi trạng thái hồ sơ.`); if (isStaff || isApplicant) await load(); }} />}
  </div>;
}

function MajorTable({ rows, onApply }: { rows: Major[]; onApply: (majorId: string) => void }) {
  if (!rows.length) return <EmptyState icon={<Search size={22} />} title="Không tìm thấy ngành phù hợp" description="Thử thay đổi nội dung tìm kiếm." />;
  return <div className="major-card-grid">{rows.map(major => <article key={major.id} className="major-card"><div className="major-card-head"><div className="major-code">{major.code}</div></div><h3>{major.name}</h3><div className="major-faculty">{major.faculty_name}</div><p>{major.description}</p><div className="major-card-bottom"><button className="icon-text-button" onClick={() => onApply(major.id)}>Tạo hồ sơ <ArrowRight size={15} /></button></div></article>)}</div>;
}

function ApplicationTable({ rows, isBusy, notes, onNoteChange, onStatus, onPromote }: { rows: Applicant[]; isBusy: string; notes: Record<string, string>; onNoteChange: (id: string, note: string) => void; onStatus: (row: Applicant, status: string, note?: string) => void; onPromote: (row: Applicant) => void }) {
  if (!rows.length) return <EmptyState icon={<FilePlus2 size={22} />} title="Chưa có hồ sơ xét tuyển" description="Hồ sơ đăng ký mới sẽ xuất hiện tại đây." />;
  return <div className="table-panel"><div className="responsive-table"><table><thead><tr><th>Thí sinh</th><th>Ngành đăng ký</th><th>Phương thức</th><th>Ngày tiếp nhận</th><th>Trạng thái</th><th>Ghi chú xử lý</th><th>Thao tác</th></tr></thead><tbody>{rows.map(row => <tr key={row.id}><td><div className="person-cell"><span className="avatar small-avatar">{row.full_name[0]}</span><span><strong>{row.full_name}</strong><small>{row.email}</small></span></div></td><td>{row.major_name}</td><td>{row.admission_method}</td><td>{new Date(row.created_at).toLocaleDateString("vi-VN")}</td><td><StatusBadge>{row.status}</StatusBadge></td><td><textarea className="applicant-note-field" rows={2} maxLength={1000} value={notes[row.id] ?? row.review_note} onChange={event => onNoteChange(row.id, event.target.value)} aria-label={`Ghi chú cho ${row.full_name}`} placeholder="Ghi chú gửi thí sinh…" /></td><td><div className="row-actions">{row.status !== "Trúng tuyển" && <select aria-label={`Cập nhật ${row.full_name}`} disabled={isBusy === row.id} value={row.status} onChange={event => onStatus(row, event.target.value)}><option>Mới tiếp nhận</option><option>Đang xét duyệt</option><option>Cần bổ sung</option><option>Đã duyệt</option><option>Trúng tuyển</option><option>Không đủ điều kiện</option><option>Không trúng tuyển</option></select>}<button className="mini-button" disabled={isBusy === row.id} onClick={() => onStatus(row, row.status, notes[row.id] ?? row.review_note)}>Lưu ghi chú</button>{row.status === "Trúng tuyển" && <button className="mini-button" disabled={isBusy === row.id} onClick={() => onPromote(row)}>{row.student_id ? "Đã chuyển" : "Tạo hồ sơ SV"}</button>}</div></td></tr>)}</tbody></table></div></div>;
}

function ApplicantApplications({ rows }: { rows: Applicant[] }) {
  if (!rows.length) return <EmptyState icon={<FilePlus2 size={22} />} title="Chưa có hồ sơ" description="Tạo hồ sơ để bắt đầu theo dõi quá trình tiếp nhận." />;
  return <div className="applicant-status-list">{rows.map(row => <article key={row.id}><div className="applicant-status-heading"><div><small>MÃ HỒ SƠ · {row.id.slice(0, 8).toUpperCase()}</small><h2>{row.major_name}</h2></div><StatusBadge>{row.status}</StatusBadge></div><div className="applicant-status-details"><span>Phương thức<strong>{row.admission_method}</strong></span><span>Ngày tiếp nhận<strong>{new Date(row.created_at).toLocaleDateString("vi-VN")}</strong></span><span>Email liên hệ<strong>{row.email}</strong></span></div>{row.review_note && <p className="applicant-review-note"><strong>Ghi chú từ bộ phận tuyển sinh</strong>{row.review_note}</p>}</article>)}</div>;
}

function ApplicationDialog({ majors, initialMajorId, onClose, onCreated }: { majors: Major[]; initialMajorId: string; onClose: () => void; onCreated: (code: string) => void }) {
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const { user } = useAuth();
  const { register, handleSubmit, setValue, formState: { errors } } = useForm<ApplicationValues>({ resolver: zodResolver(applicationSchema), defaultValues: { admission_method: "Học bạ", desired_major_id: initialMajorId } });
  useEffect(() => { if (initialMajorId) setValue("desired_major_id", initialMajorId); }, [initialMajorId, setValue]);
  const submit = async (values: ApplicationValues) => {
    if (!user && (values.password?.length ?? 0) < 8) { setError("Tạo mật khẩu có ít nhất 8 ký tự để theo dõi hồ sơ."); return; }
    setBusy(true); setError("");
    try { const payload = { ...values }; if (user?.role === "applicant") delete payload.password; const row = await api<{ id: string }>("/admissions/applications", { method: "POST", body: JSON.stringify(payload) }); onCreated(row.id.slice(0, 8).toUpperCase()); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Không thể tiếp nhận hồ sơ."); }
    finally { setBusy(false); }
  };
  return <div className="modal-backdrop" onClick={onClose}><section className="form-modal" role="dialog" aria-modal="true" onClick={event => event.stopPropagation()}><div className="modal-heading"><div><div className="eyebrow">TUYỂN SINH</div><h2>Tạo hồ sơ đăng ký</h2><p>Thông tin sẽ được tiếp nhận để theo dõi quá trình xử lý.</p></div><button className="modal-close" onClick={onClose} aria-label="Đóng"><X size={18} /></button></div>
    <form className="form-stack" onSubmit={handleSubmit(submit)}><label>Họ và tên<input {...register("full_name")} placeholder="Nguyễn Văn A" />{errors.full_name && <small className="field-error">{errors.full_name.message}</small>}</label><div className="form-row"><label>Email<input type="email" {...register("email")} placeholder="ban@example.com" />{errors.email && <small className="field-error">{errors.email.message}</small>}</label><label>Số điện thoại<input {...register("phone")} placeholder="09xx xxx xxx" />{errors.phone && <small className="field-error">{errors.phone.message}</small>}</label></div>{!user && <label>Mật khẩu đăng nhập<input type="password" {...register("password")} minLength={8} autoComplete="new-password" required />{errors.password && <small className="field-error">{errors.password.message}</small>}</label>}<label>Ngành đăng ký<select id="desired_major_id" {...register("desired_major_id")} defaultValue=""><option value="" disabled>Chọn ngành đào tạo</option>{majors.map(major => <option key={major.id} value={major.id}>{major.name} · {major.code}</option>)}</select>{errors.desired_major_id && <small className="field-error">{errors.desired_major_id.message}</small>}</label><label>Phương thức xét tuyển<select {...register("admission_method")}><option>Học bạ</option><option>Điểm thi tốt nghiệp THPT</option><option>Xét tuyển kết hợp</option></select></label>
      {error && <div className="inline-error">{error}</div>}<div className="modal-actions"><button type="button" className="button button-ghost" onClick={onClose}>Hủy</button><button className="button button-primary" disabled={busy}>{busy ? "Đang gửi…" : "Gửi hồ sơ"}<ArrowRight size={15} /></button></div></form>
  </section></div>;
}
