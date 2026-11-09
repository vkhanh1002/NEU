"use client";

import { FormEvent, Fragment, useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import { ArrowLeft, ArrowRight, Check, ChevronDown, ChevronUp, FilePlus2, Plus, Search, X } from "lucide-react";
import { api, Major } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { EmptyState, ErrorNotice, Loading, PageTitle, StatusBadge } from "@/components/ui";
import { ApplicantDocumentManager, APPLICANT_DOCUMENT_TYPES, SelectedFilePreview } from "@/features/applicant-documents";

type Applicant = { id: string; email: string; full_name: string; phone: string; desired_major_id: string; major_name: string; admission_method: string; status: string; review_note: string; created_at: string; student_id: string | null; preferences?: { major_id: string; major_name: string; preference_order: number; admission_method: string }[] };
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
    {loading ? <Loading /> : isApplicant ? <ApplicantApplications rows={applications} /> : tab === "majors" ? <MajorTable rows={visibleMajors} canApply={!user || isApplicant} onApply={majorId => { setSelectedMajor(majorId); setShowForm(true); }} /> : isStaff ? <ApplicationTable rows={visibleApplications} isBusy={busyId} notes={reviewNotes} onNoteChange={(id, note) => setReviewNotes(current => ({ ...current, [id]: note }))} onStatus={updateStatus} onPromote={promote} /> : <EmptyState title="Đăng nhập để xem hồ sơ" description="Danh sách hồ sơ xét tuyển chỉ hiển thị cho nhân viên được phân quyền." />}
    {showForm && <ApplicationDialog majors={majors} initialMajorId={selectedMajor} onClose={() => setShowForm(false)} onCreated={async (code, notice) => { setShowForm(false); setMessage(`Đã tiếp nhận hồ sơ ${code}.${notice ? ` ${notice}` : ""}`); if (isStaff || isApplicant) await load(); }} />}
  </div>;
}

function MajorTable({ rows, canApply, onApply }: { rows: Major[]; canApply: boolean; onApply: (majorId: string) => void }) {
  if (!rows.length) return <EmptyState icon={<Search size={22} />} title="Không tìm thấy ngành phù hợp" description="Thử thay đổi nội dung tìm kiếm." />;
  return <div className="major-card-grid">{rows.map(major => <article key={major.id} className="major-card"><div className="major-card-head"><div className="major-code">{major.code}</div></div><h3>{major.name}</h3><div className="major-faculty">{major.faculty_name}</div><p>{major.description}</p><div className="major-card-bottom">{canApply && major.admission_status === "Đang tuyển sinh" ? <button className="icon-text-button" onClick={() => onApply(major.id)}>Tạo hồ sơ <ArrowRight size={15} /></button> : <span className="major-status-label">{major.admission_status === "Đang tuyển sinh" ? "Đăng nhập bằng tài khoản thí sinh để đăng ký" : major.admission_status}</span>}</div></article>)}</div>;
}

function ApplicationTable({ rows, isBusy, notes, onNoteChange, onStatus, onPromote }: { rows: Applicant[]; isBusy: string; notes: Record<string, string>; onNoteChange: (id: string, note: string) => void; onStatus: (row: Applicant, status: string, note?: string) => void; onPromote: (row: Applicant) => void }) {
  if (!rows.length) return <EmptyState icon={<FilePlus2 size={22} />} title="Chưa có hồ sơ xét tuyển" description="Hồ sơ đăng ký mới sẽ xuất hiện tại đây." />;
  return <div className="table-panel"><div className="responsive-table"><table><thead><tr><th>Thí sinh</th><th>Ngành đăng ký</th><th>Phương thức</th><th>Ngày tiếp nhận</th><th>Trạng thái</th><th>Ghi chú xử lý</th><th>Thao tác</th></tr></thead><tbody>{rows.map(row => <Fragment key={row.id}><tr><td><div className="person-cell"><span className="avatar small-avatar">{row.full_name[0]}</span><span><strong>{row.full_name}</strong><small>{row.email}</small></span></div></td><td>{row.major_name}{row.preferences && row.preferences.length > 1 && <small className="preference-count">{row.preferences.length} nguyện vọng</small>}</td><td>{row.admission_method}</td><td>{new Date(row.created_at).toLocaleDateString("vi-VN")}</td><td><StatusBadge>{row.status}</StatusBadge></td><td><textarea className="applicant-note-field" rows={2} maxLength={1000} value={notes[row.id] ?? row.review_note} onChange={event => onNoteChange(row.id, event.target.value)} aria-label={`Ghi chú cho ${row.full_name}`} placeholder="Ghi chú gửi thí sinh…" /></td><td><div className="row-actions">{row.status !== "Trúng tuyển" && <select aria-label={`Cập nhật ${row.full_name}`} disabled={isBusy === row.id} value={row.status} onChange={event => onStatus(row, event.target.value)}><option>Mới tiếp nhận</option><option>Đang xét duyệt</option><option>Cần bổ sung</option><option>Đã duyệt</option><option>Trúng tuyển</option><option>Không đủ điều kiện</option><option>Không trúng tuyển</option></select>}<button className="mini-button" disabled={isBusy === row.id} onClick={() => onStatus(row, row.status, notes[row.id] ?? row.review_note)}>Lưu ghi chú</button>{row.status === "Trúng tuyển" && <button className="mini-button" disabled={isBusy === row.id} onClick={() => onPromote(row)}>{row.student_id ? "Đã chuyển" : "Tạo hồ sơ SV"}</button>}</div></td></tr><tr><td colSpan={7}><ApplicantDocumentManager applicantId={row.id} isStaff /></td></tr></Fragment>)}</tbody></table></div></div>;
}

function ApplicantApplications({ rows }: { rows: Applicant[] }) {
  if (!rows.length) return <EmptyState icon={<FilePlus2 size={22} />} title="Chưa có hồ sơ" description="Tạo hồ sơ để bắt đầu theo dõi quá trình tiếp nhận." />;
  return <div className="applicant-status-list">{rows.map(row => <article key={row.id}><div className="applicant-status-heading"><div><small>MÃ HỒ SƠ · {row.id.slice(0, 8).toUpperCase()}</small><h2>{row.major_name}</h2></div><StatusBadge>{row.status}</StatusBadge></div><div className="applicant-status-details"><span>Phương thức<strong>{row.admission_method}</strong></span><span>Ngày tiếp nhận<strong>{new Date(row.created_at).toLocaleDateString("vi-VN")}</strong></span><span>Email liên hệ<strong>{row.email}</strong></span></div>{row.preferences && row.preferences.length > 1 && <div className="applicant-preferences"><strong>Thứ tự nguyện vọng</strong>{row.preferences.map(item => <span key={item.major_id}>{item.preference_order}. {item.major_name}</span>)}</div>}{row.review_note && <p className="applicant-review-note"><strong>Ghi chú từ bộ phận tuyển sinh</strong>{row.review_note}</p>}<ApplicantDocumentManager applicantId={row.id} isStaff={false} /></article>)}</div>;
}

function ApplicationDialog({ majors, initialMajorId, onClose, onCreated }: { majors: Major[]; initialMajorId: string; onClose: () => void; onCreated: (code: string, notice?: string) => void }) {
  const { user, login } = useAuth();
  const activeMajors = majors.filter(major => major.admission_status === "Đang tuyển sinh");
  const [step, setStep] = useState(0);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [confirmed, setConfirmed] = useState(false);
  const [personal, setPersonal] = useState({ full_name: user?.full_name ?? "", email: user?.email ?? "", password: "", phone: "", date_of_birth: "", gender: "", identity_number: "", identity_issue_date: "", identity_issue_place: "", nationality: "Việt Nam", ethnicity: "", address: "", permanent_address: "", emergency_name: "", emergency_phone: "", emergency_relationship: "" });
  const [education, setEducation] = useState({ high_school: "", high_school_province: "", graduation_year: "2026", high_school_gpa: "", conduct: "", subject_scores: "", admission_method: "Học bạ" });
  const [preferences, setPreferences] = useState<string[]>(initialMajorId ? [initialMajorId] : []);
  const [files, setFiles] = useState<Record<string, File>>({});
  useEffect(() => {
    setPreferences(current => initialMajorId ? [initialMajorId, ...current.filter(id => id !== initialMajorId)] : current);
  }, [initialMajorId]);
  useEffect(() => {
    if (user?.role === "applicant") setPersonal(current => ({ ...current, email: user.email, full_name: current.full_name || user.full_name }));
  }, [user]);
  const changePersonal = (key: string, value: string) => setPersonal(current => ({ ...current, [key]: value }));
  const changeEducation = (key: string, value: string) => setEducation(current => ({ ...current, [key]: value }));

  function validateStep() {
    if (step === 0) {
      if (personal.full_name.trim().length < 2) return "Nhập đầy đủ họ và tên.";
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(personal.email)) return "Email chưa đúng định dạng.";
      if (personal.phone.replace(/\D/g, "").length < 8) return "Nhập số điện thoại hợp lệ.";
      if (!user && personal.password.length < 8) return "Tạo mật khẩu có ít nhất 8 ký tự để theo dõi hồ sơ.";
    }
    if (step === 2 && preferences.length === 0) return "Chọn ít nhất một nguyện vọng.";
    if (step === 4 && !confirmed) return "Vui lòng xác nhận thông tin trước khi gửi hồ sơ.";
    return "";
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const validationError = validateStep();
    if (validationError) { setError(validationError); return; }
    if (step < 4) { setStep(current => current + 1); setError(""); return; }
    setBusy(true); setError("");
    try {
      const payload = {
        full_name: personal.full_name.trim(), email: personal.email.trim().toLowerCase(),
        ...(user ? {} : { password: personal.password }), phone: personal.phone.trim(),
        date_of_birth: personal.date_of_birth || null, address: personal.address.trim(),
        desired_major_id: preferences[0], admission_method: education.admission_method,
        preferences, confirmed: true,
        details: {
          gender: personal.gender, identity_number: personal.identity_number,
          identity_issue_date: personal.identity_issue_date, identity_issue_place: personal.identity_issue_place,
          nationality: personal.nationality, ethnicity: personal.ethnicity,
          permanent_address: personal.permanent_address, emergency_name: personal.emergency_name,
          emergency_phone: personal.emergency_phone, emergency_relationship: personal.emergency_relationship,
          high_school: education.high_school, high_school_province: education.high_school_province,
          graduation_year: education.graduation_year, high_school_gpa: education.high_school_gpa,
          conduct: education.conduct, subject_scores: education.subject_scores,
        },
      };
      const row = await api<{ id: string }>("/admissions/applications", { method: "POST", body: JSON.stringify(payload) });
      let notice = "";
      if (!user) {
        try { await login(payload.email, personal.password); }
        catch { notice = "Hồ sơ đã được tiếp nhận nhưng chưa tự đăng nhập được. Dùng email và mật khẩu vừa tạo để đăng nhập."; }
      }
      const failedUploads: string[] = [];
      for (const [documentType, file] of Object.entries(files)) {
        const body = new FormData(); body.set("document_type", documentType); body.set("file", file);
        try { await api(`/admissions/applications/${row.id}/documents`, { method: "POST", body }); }
        catch { failedUploads.push(file.name); }
      }
      if (failedUploads.length) notice = `${notice ? `${notice} ` : ""}Hồ sơ đã được tiếp nhận; chưa tải được ${failedUploads.join(", ")}. Có thể tải bổ sung trong mục Tài liệu hồ sơ.`;
      else if (files && Object.keys(files).length) notice = `${notice ? `${notice} ` : ""}Đã nhận ${Object.keys(files).length} tài liệu.`;
      onCreated(row.id.slice(0, 8).toUpperCase(), notice || undefined);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Không thể tiếp nhận hồ sơ.");
    } finally { setBusy(false); }
  }

  function chooseFile(type: string, selected: File | undefined) {
    setError("");
    if (!selected) { setFiles(current => { const next = { ...current }; delete next[type]; return next; }); return; }
    const ext = `.${selected.name.split(".").pop()?.toLowerCase() ?? ""}`;
    if (![".pdf", ".docx", ".png", ".jpg", ".jpeg"].includes(ext)) { setError("Chỉ nhận PDF, DOCX, PNG hoặc JPG/JPEG."); return; }
    if (selected.size > 10 * 1024 * 1024) { setError("Mỗi tài liệu có dung lượng tối đa 10 MB."); return; }
    setFiles(current => ({ ...current, [type]: selected }));
  }

  const methodSuggestions = education.admission_method === "Học bạ" ? ["transcript", "graduation_proof"] : education.admission_method === "Điểm thi tốt nghiệp THPT" ? ["exam_result", "graduation_proof"] : ["transcript", "exam_result"];
  const labels = ["Cá nhân", "Học vấn", "Nguyện vọng", "Tài liệu", "Xác nhận"];
  const displayName = (id: string) => activeMajors.find(item => item.id === id)?.name ?? id;
  const movePreference = (index: number, direction: -1 | 1) => setPreferences(current => {
    const target = index + direction; if (target < 0 || target >= current.length) return current;
    const next = [...current]; [next[index], next[target]] = [next[target], next[index]]; return next;
  });

  return <div className="modal-backdrop" onClick={() => { if (!busy) onClose(); }}><section className="form-modal application-wizard" role="dialog" aria-modal="true" aria-labelledby="application-dialog-title" onClick={event => event.stopPropagation()}>
    <div className="modal-heading"><div><div className="eyebrow">TUYỂN SINH · HỒ SƠ TRỰC TUYẾN</div><h2 id="application-dialog-title">Tạo hồ sơ đăng ký</h2><p>Hoàn thành từng bước. Bạn có thể bổ sung tài liệu sau khi gửi hồ sơ.</p></div><button className="modal-close" onClick={onClose} disabled={busy} aria-label="Đóng"><X size={18} /></button></div>
    <div className="wizard-progress" aria-label={`Bước ${step + 1} trên 5`}>{labels.map((label, index) => <button type="button" key={label} className={index === step ? "current" : index < step ? "complete" : ""} onClick={() => { if (index <= step) { setStep(index); setError(""); } }}><span>{index < step ? <Check size={15} /> : index + 1}</span>{label}</button>)}</div>
    <form className="form-stack" onSubmit={submit}>
      {step === 0 && <section className="wizard-section"><h3>Thông tin cá nhân và liên hệ</h3><p>Thông tin này được lưu trong hồ sơ tuyển sinh của bạn.</p><div className="form-row"><label>Họ và tên *<input autoComplete="name" value={personal.full_name} onChange={event => changePersonal("full_name", event.target.value)} placeholder="Nguyễn Văn A" /></label><label>Ngày sinh<input type="date" value={personal.date_of_birth} onChange={event => changePersonal("date_of_birth", event.target.value)} /></label></div><div className="form-row"><label>Email *<input type="email" autoComplete="email" value={personal.email} onChange={event => changePersonal("email", event.target.value)} readOnly={user?.role === "applicant"} placeholder="ban@example.com" /></label><label>Số điện thoại *<input type="tel" autoComplete="tel" value={personal.phone} onChange={event => changePersonal("phone", event.target.value)} placeholder="09xx xxx xxx" /></label></div>{!user && <label>Mật khẩu theo dõi hồ sơ *<input type="password" minLength={8} autoComplete="new-password" value={personal.password} onChange={event => changePersonal("password", event.target.value)} placeholder="Ít nhất 8 ký tự" /><small>Sau khi gửi hồ sơ, bạn sẽ được đăng nhập để theo dõi trạng thái.</small></label>}<div className="form-row"><label>Giới tính<input value={personal.gender} onChange={event => changePersonal("gender", event.target.value)} placeholder="Tùy chọn" /></label><label>Quốc tịch<input value={personal.nationality} onChange={event => changePersonal("nationality", event.target.value)} /></label></div><div className="form-row"><label>Số CCCD/CMND<input value={personal.identity_number} onChange={event => changePersonal("identity_number", event.target.value)} /></label><label>Dân tộc<input value={personal.ethnicity} onChange={event => changePersonal("ethnicity", event.target.value)} /></label></div><div className="form-row"><label>Ngày cấp CCCD<input type="date" value={personal.identity_issue_date} onChange={event => changePersonal("identity_issue_date", event.target.value)} /></label><label>Nơi cấp<input value={personal.identity_issue_place} onChange={event => changePersonal("identity_issue_place", event.target.value)} /></label></div><label>Địa chỉ hiện tại<input value={personal.address} onChange={event => changePersonal("address", event.target.value)} /></label><label>Địa chỉ thường trú<input value={personal.permanent_address} onChange={event => changePersonal("permanent_address", event.target.value)} /></label><h4>Người liên hệ khi cần</h4><div className="form-row"><label>Họ tên người liên hệ<input value={personal.emergency_name} onChange={event => changePersonal("emergency_name", event.target.value)} /></label><label>Số điện thoại<input value={personal.emergency_phone} onChange={event => changePersonal("emergency_phone", event.target.value)} /></label></div><label>Quan hệ<input value={personal.emergency_relationship} onChange={event => changePersonal("emergency_relationship", event.target.value)} /></label></section>}

      {step === 1 && <section className="wizard-section"><h3>Quá trình học tập</h3><p>Khai báo thông tin học tập hiện có. Có thể để trống trường chưa biết.</p><label>Trường THPT<input value={education.high_school} onChange={event => changeEducation("high_school", event.target.value)} /></label><div className="form-row"><label>Tỉnh/thành phố<select value={education.high_school_province} onChange={event => changeEducation("high_school_province", event.target.value)}><option value="">Chọn tỉnh/thành phố</option>{["Hà Nội", "Hồ Chí Minh", "Đà Nẵng", "Cần Thơ", "Hải Phòng", "Nghệ An", "Thanh Hóa", "Khác"].map(item => <option key={item}>{item}</option>)}</select></label><label>Năm tốt nghiệp<input type="number" min="2000" max="2035" value={education.graduation_year} onChange={event => changeEducation("graduation_year", event.target.value)} /></label></div><div className="form-row"><label>Điểm trung bình học bạ<input type="number" min="0" max="10" step="0.01" value={education.high_school_gpa} onChange={event => changeEducation("high_school_gpa", event.target.value)} /></label><label>Hạnh kiểm<input value={education.conduct} onChange={event => changeEducation("conduct", event.target.value)} /></label></div><label>Điểm môn / ghi chú học tập<textarea rows={3} value={education.subject_scores} onChange={event => changeEducation("subject_scores", event.target.value)} placeholder="Có thể bổ sung điểm môn theo thông báo tuyển sinh." /></label><label>Phương thức xét tuyển<select value={education.admission_method} onChange={event => changeEducation("admission_method", event.target.value)}><option>Học bạ</option><option>Điểm thi tốt nghiệp THPT</option><option>Xét tuyển kết hợp</option></select></label></section>}

      {step === 2 && <section className="wizard-section"><h3>Ngành và thứ tự nguyện vọng</h3><p>Nguyện vọng đầu tiên là ngành đăng ký chính. Dùng các nút mũi tên để đổi thứ tự.</p><div className="preference-list">{preferences.map((id, index) => <div className="preference-item" key={`${index}-${id}`}><strong>{index + 1}</strong><select value={id} onChange={event => setPreferences(current => current.map((item, at) => at === index ? event.target.value : item))}><option value="">Chọn ngành</option>{activeMajors.filter(major => !preferences.includes(major.id) || major.id === id).map(major => <option key={major.id} value={major.id}>{major.name} · {major.code}</option>)}</select><button type="button" className="mini-button" aria-label="Đưa lên" disabled={index === 0} onClick={() => movePreference(index, -1)}><ChevronUp size={16} /></button><button type="button" className="mini-button" aria-label="Đưa xuống" disabled={index === preferences.length - 1} onClick={() => movePreference(index, 1)}><ChevronDown size={16} /></button><button type="button" className="mini-button danger-mini" aria-label="Xóa nguyện vọng" onClick={() => setPreferences(current => current.filter((_, at) => at !== index))}><X size={16} /></button></div>)}</div><button type="button" className="button button-secondary" disabled={preferences.length >= 10 || activeMajors.length <= preferences.length} onClick={() => setPreferences(current => [...current, activeMajors.find(item => !current.includes(item.id))?.id ?? ""])}><Plus size={16} /> Thêm nguyện vọng</button></section>}

      {step === 3 && <section className="wizard-section"><h3>Tài liệu đính kèm</h3><p>Tài liệu là tùy chọn. Chỉ gửi giấy tờ phù hợp với hồ sơ của bạn; mỗi tệp tối đa 10 MB.</p><div className="document-recommendation"><strong>Tài liệu gợi ý theo phương thức: {education.admission_method}</strong><span>{methodSuggestions.map(type => APPLICANT_DOCUMENT_TYPES.find(item => item.id === type)?.label).join(" · ")}</span><small>Danh sách chỉ để chuẩn bị; vui lòng đối chiếu thông báo tuyển sinh chính thức.</small></div><div className="wizard-document-grid">{APPLICANT_DOCUMENT_TYPES.map(item => <div className="wizard-document-card" key={item.id} onDragOver={event => event.preventDefault()} onDrop={event => { event.preventDefault(); chooseFile(item.id, event.dataTransfer.files?.[0]); }}><strong>{item.label}</strong><span>PDF, DOCX, PNG hoặc JPG/JPEG · tối đa 10 MB</span><label>Chọn tệp<input key={`${item.id}-${files[item.id] ? "selected" : "empty"}`} type="file" accept=".pdf,.docx,.png,.jpg,.jpeg" onChange={event => chooseFile(item.id, event.target.files?.[0])} /></label>{files[item.id] ? <div className="file-preview-row"><SelectedFilePreview file={files[item.id]} /><button type="button" className="mini-button danger-mini" onClick={() => chooseFile(item.id, undefined)}>Xóa</button></div> : <small>Chọn hoặc kéo tệp vào đây</small>}</div>)}</div></section>}

      {step === 4 && <section className="wizard-section"><h3>Kiểm tra và xác nhận</h3><p>Kiểm tra lại trước khi gửi. Hồ sơ có thể được bổ sung theo yêu cầu của bộ phận tuyển sinh.</p><div className="application-review"><div><strong>Thí sinh</strong><span>{personal.full_name} · {personal.email} · {personal.phone}</span></div><div><strong>Học vấn</strong><span>{education.high_school || "Chưa khai báo trường THPT"} · Năm tốt nghiệp {education.graduation_year || "—"}</span></div><div><strong>Phương thức</strong><span>{education.admission_method}</span></div><div><strong>Nguyện vọng</strong>{preferences.map((id, index) => <span key={`${index}-${id}`}>{index + 1}. {displayName(id)}</span>)}</div><div><strong>Tài liệu đã chọn</strong><span>{Object.values(files).length ? Object.values(files).map(file => file.name).join(" · ") : "Chưa chọn tài liệu — có thể tải bổ sung sau"}</span></div></div><label className="consent-checkbox"><input type="checkbox" checked={confirmed} onChange={event => setConfirmed(event.target.checked)} /><span>Tôi xác nhận thông tin đã khai báo là chính xác và đồng ý gửi hồ sơ để NEU xem xét.</span></label></section>}

      {error && <div className="inline-error">{error}</div>}
      <div className="modal-actions wizard-actions"><button type="button" className="button button-ghost" onClick={step ? () => { setStep(current => current - 1); setError(""); } : onClose} disabled={busy}>{step ? <><ArrowLeft size={15} /> Quay lại</> : "Hủy"}</button><span>Bước {step + 1} / 5</span><button className="button button-primary" disabled={busy}>{busy ? "Đang gửi…" : step === 4 ? "Gửi hồ sơ" : "Tiếp tục"}<ArrowRight size={15} /></button></div>
    </form>
  </section></div>;
}
