"use client";

import { useEffect, useRef, useState } from "react";
import { Bot, Check, FileText, LoaderCircle, Plus, RefreshCw, ShieldAlert, Trash2, UploadCloud, Globe } from "lucide-react";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { EmptyState, ErrorNotice, Loading, PageTitle, StatusBadge } from "@/components/ui";

type Document = { id: string; filename: string; media_type: string; status: string; is_public: boolean; error: string | null; created_at: string };
type FAQ = { id: string; question: string; answer: string; category: string; is_published: boolean };
type AIStatus = { llm_configured: boolean; configured: boolean; provider: string; model: string; fallback_provider: string | null; fallback_configured: boolean; embedding_model: string | null; embedding_provider: string; retrieval_mode: string };
type AIConnectionResult = { ok: boolean; provider: string; model?: string; used_fallback?: boolean; status_code?: number | null; error_code?: string; checked_at: string };
type AIMetric = { created_at: string; provider: string | null; model: string | null; retrieval_seconds: number; provider_seconds?: number; ttft_seconds?: number; generation_seconds?: number; total_seconds: number; input_tokens?: number; output_tokens?: number; retry_count: number; fallback_count: number; status: string; error_code?: string };
type AIMetrics = { retained_requests: number; successful_requests: number; average_total_seconds: number | null; recent: AIMetric[] };

export function KnowledgeAdmin() {
  const { user } = useAuth();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [faqs, setFaqs] = useState<FAQ[]>([]);
  const [aiStatus, setAiStatus] = useState<AIStatus | null>(null);
  const [aiMetrics, setAiMetrics] = useState<AIMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [faqOpen, setFaqOpen] = useState(false);
  const [checkingAI, setCheckingAI] = useState(false);
  const [aiCheck, setAiCheck] = useState<AIConnectionResult | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);
  const isAdmin = user?.role === "super_admin";
  async function load() {
    setError("");
    try {
      const [docs, faqRows, status, metrics] = await Promise.all([
        api<Document[]>("/admin/knowledge-documents"), api<FAQ[]>("/admin/faqs"), api<AIStatus>("/admin/ai-status"),
        api<AIMetrics>("/admin/ai-metrics"),
      ]);
      setDocuments(docs); setFaqs(faqRows); setAiStatus(status); setAiMetrics(metrics);
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Không thể tải kho tri thức."); }
    finally { setLoading(false); }
  }
  useEffect(() => { if (user?.role === "super_admin") void load(); else setLoading(false); }, [user]);
  async function upload(file?: File) {
    if (!file) return;
    setBusy(true); setError(""); setNotice("");
    try { const body = new FormData(); body.set("file", file); await api("/admin/knowledge-documents", { method: "POST", body }); setNotice(`Đã xử lý tài liệu “${file.name}”.`); await load(); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Không tải được tài liệu."); }
    finally { setBusy(false); if (fileRef.current) fileRef.current.value = ""; }
  }
  async function removeDocument(doc: Document) {
    if (!window.confirm(`Xóa tài liệu “${doc.filename}” khỏi kho tri thức?`)) return;
    try { await api(`/admin/knowledge-documents/${doc.id}`, { method: "DELETE" }); setDocuments(current => current.filter(item => item.id !== doc.id)); setNotice("Đã xóa tài liệu và các đoạn tri thức liên quan."); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Không xóa được tài liệu."); }
  }
  async function toggleDocumentVisibility(doc: Document) {
    try {
      const updated = await api<Document>(`/admin/knowledge-documents/${doc.id}/visibility`, { method: "PATCH", body: JSON.stringify({ is_public: !doc.is_public }) });
      setDocuments(current => current.map(item => item.id === doc.id ? updated : item));
      setNotice(updated.is_public ? "Tài liệu đã được cho phép truy xuất công khai." : "Tài liệu đã được ẩn khỏi tìm kiếm Guest.");
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Không cập nhật được phạm vi tài liệu."); }
  }
  async function removeFaq(faq: FAQ) {
    if (!window.confirm("Xóa câu hỏi thường gặp này?")) return;
    try { await api(`/admin/faqs/${faq.id}`, { method: "DELETE" }); setFaqs(current => current.filter(item => item.id !== faq.id)); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Không xóa được FAQ."); }
  }
  async function checkAI() {
    setCheckingAI(true); setAiCheck(null);
    try { setAiCheck(await api<AIConnectionResult>("/admin/ai-status/check", { method: "POST" })); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Không kiểm tra được dịch vụ AI."); }
    finally { setCheckingAI(false); }
  }
  if (!user || !isAdmin) return <div className="module-page"><PageTitle eyebrow="QUẢN TRỊ" title="Kho tri thức" description="Quản lý tài liệu nguồn và trạng thái tích hợp AI." /><EmptyState icon={<ShieldAlert size={23} />} title={user ? "Không đủ quyền truy cập" : "Đăng nhập với quyền quản trị"} description="Kho tri thức và cấu hình AI chỉ dành cho Super Admin. API cũng kiểm tra quyền trên mọi thao tác." /></div>;
  const hasConfiguredProvider = Boolean(aiStatus?.configured || aiStatus?.fallback_configured);
  const providerSummary = aiStatus?.configured
    ? `Chính: ${aiStatus.provider} · ${aiStatus.model}`
    : aiStatus?.fallback_configured
      ? `Provider chính chưa cấu hình · Dự phòng khả dụng: ${aiStatus.fallback_provider}`
      : "Chưa cấu hình API key cho provider đang chọn. Assistant vẫn tìm FAQ và tài liệu bằng từ khóa.";
  return <div className="module-page">
    <PageTitle eyebrow="QUẢN TRỊ AI" title="Kho tri thức" description="Nạp tài liệu để trợ lý NEU tra cứu và trả lời có căn cứ." action={<button className="button button-secondary" onClick={() => void load()}><RefreshCw size={15} /> Làm mới</button>} />
    <div className="module-notice"><Bot size={16} /><span>API key được giữ ở backend. Chỉ tải lên tài liệu phù hợp để dùng với nhà cung cấp AI bên ngoài. RAG hiện hỗ trợ tìm kiếm từ khóa.</span></div>
    {error && <ErrorNotice message={error} />}{notice && <div className="success-notice"><Check size={16} />{notice}</div>}
    {loading ? <Loading /> : <>
      <section className="ai-config-card"><div className="ai-config-icon"><Bot size={20} /></div><div className="ai-config-copy"><div className="eyebrow">AI SERVICE</div><h2>{hasConfiguredProvider ? (aiStatus?.configured ? `Provider: ${aiStatus.provider}` : `Dự phòng: ${aiStatus?.fallback_provider}`) : "Chế độ chỉ tra cứu tài liệu"}</h2><p>{hasConfiguredProvider ? `${providerSummary} · Dự phòng: ${aiStatus?.fallback_configured ? aiStatus.fallback_provider : "chưa cấu hình"} · Retrieval: ${aiStatus?.retrieval_mode}` : providerSummary}{aiCheck && <><br />{aiCheck.ok ? `Kiểm tra ${new Date(aiCheck.checked_at).toLocaleTimeString("vi-VN")}: kết nối ${aiCheck.provider} thành công với ${aiCheck.model}${aiCheck.used_fallback ? " (đang dùng provider dự phòng)" : ""}.` : `Kiểm tra thất bại: ${aiCheck.provider} · HTTP ${aiCheck.status_code ?? "—"} · ${aiCheck.error_code}.`}</>}</p></div><div className="ai-config-actions"><StatusBadge>{hasConfiguredProvider ? "Đã cấu hình" : "Chưa cấu hình"}</StatusBadge><button className="button button-secondary button-small" onClick={() => void checkAI()} disabled={checkingAI}>{checkingAI ? "Đang kiểm tra…" : "Kiểm tra kết nối"}</button></div></section>
      <section className="knowledge-panel ai-metrics-panel"><div className="section-heading"><div><h2>Hiệu năng trợ lý</h2><p>Số liệu backend hiện tại · lưu tối đa 200 lượt trong bộ nhớ tiến trình</p></div><span className="count-pill">{aiMetrics?.retained_requests ?? 0} lượt</span></div><div className="ai-metrics-summary"><span>Thành công: <strong>{aiMetrics?.successful_requests ?? 0}</strong></span><span>TB tổng thời gian: <strong>{aiMetrics?.average_total_seconds == null ? "—" : `${aiMetrics.average_total_seconds}s`}</strong></span></div>{aiMetrics?.recent.length ? <div className="ai-metric-list">{aiMetrics.recent.slice(0, 10).map((metric, index) => <div className="ai-metric-row" key={`${metric.created_at}-${index}`}><div className="ai-metric-provider"><strong>{metric.provider ?? "Không gọi LLM"}</strong><small>{metric.model ?? metric.error_code ?? "Tra cứu nội bộ"}</small></div><span>{metric.status}</span><span>RAG {metric.retrieval_seconds.toFixed(2)}s</span><span>AI {metric.provider_seconds == null ? "—" : `${metric.provider_seconds.toFixed(2)}s`}</span><span>TTFT {metric.ttft_seconds == null ? "—" : `${metric.ttft_seconds.toFixed(2)}s`}</span><span>Tổng {metric.total_seconds.toFixed(2)}s</span><span>Token {metric.input_tokens ?? "—"}/{metric.output_tokens ?? "—"}</span><span>Retry {metric.retry_count} · fallback {metric.fallback_count}</span></div>)}</div> : <div className="knowledge-empty">Chưa có lượt trò chuyện để đo. Hãy gửi câu hỏi để bắt đầu ghi nhận.</div>}</section>
      <div className="knowledge-grid"><section className="knowledge-panel"><div className="section-heading"><div><h2>Tài liệu tri thức</h2><p>PDF, DOCX, TXT hoặc Markdown · tối đa 10 MB mỗi tệp</p></div><span className="count-pill">{documents.length}</span></div>
        <div className="upload-dropzone" onClick={() => !busy && fileRef.current?.click()} onDragOver={event => event.preventDefault()} onDrop={event => { event.preventDefault(); void upload(event.dataTransfer.files[0]); }} role="button" tabIndex={0} onKeyDown={event => { if (event.key === "Enter") fileRef.current?.click(); }}><input ref={fileRef} type="file" accept=".pdf,.docx,.txt,.md,.markdown" hidden onChange={event => void upload(event.target.files?.[0])} />{busy ? <LoaderCircle className="spin" size={25} /> : <UploadCloud size={25} />}<strong>{busy ? "Đang trích xuất và lập chỉ mục…" : "Kéo thả hoặc chọn tài liệu"}</strong><span>{busy ? "Tài liệu sẽ sẵn sàng khi xử lý hoàn tất." : "PDF · DOCX · TXT · MD"}</span></div>
        {documents.length ? <div className="document-list">{documents.map(doc => <div className="document-row" key={doc.id}><span className="document-icon"><FileText size={17} /></span><span className="document-copy"><strong>{doc.filename}</strong><small>{new Date(doc.created_at).toLocaleDateString("vi-VN")}{doc.error ? ` · ${doc.error}` : ""}</small></span><StatusBadge>{doc.status === "ready" ? "Đã lập chỉ mục" : doc.status === "failed" ? "Lỗi xử lý" : "Đang xử lý"}</StatusBadge><button className={`icon-button ${doc.is_public ? "" : "subtle-danger"}`} disabled={doc.status !== "ready"} onClick={() => void toggleDocumentVisibility(doc)} title={doc.is_public ? "Guest được phép truy xuất" : "Chỉ người dùng nội bộ"} aria-label={doc.is_public ? "Ẩn tài liệu khỏi Guest" : "Cho phép Guest truy xuất"}><Globe size={15} /></button><button className="icon-button subtle-danger" onClick={() => void removeDocument(doc)} aria-label="Xóa tài liệu"><Trash2 size={15} /></button></div>)}</div> : <div className="knowledge-empty">Chưa có tài liệu được tải lên.</div>}
      </section>
      <section className="knowledge-panel faq-admin-panel"><div className="section-heading"><div><h2>Câu hỏi thường gặp</h2><p>Nguồn tra cứu được dùng kèm kho tài liệu</p></div><button className="button button-secondary button-small" onClick={() => setFaqOpen(true)}><Plus size={15} /> Thêm FAQ</button></div>{faqs.length ? <div className="faq-admin-list">{faqs.map(faq => <div className="faq-admin-row" key={faq.id}><div><strong>{faq.question}</strong><p>{faq.answer}</p><span>{faq.category}</span></div><button className="icon-button subtle-danger" onClick={() => void removeFaq(faq)} aria-label="Xóa FAQ"><Trash2 size={15} /></button></div>)}</div> : <div className="knowledge-empty">Chưa có FAQ.</div>}</section></div>
    </>}
    {faqOpen && <FAQDialog onClose={() => setFaqOpen(false)} onCreated={async () => { setFaqOpen(false); await load(); }} />}
  </div>;
}

function FAQDialog({ onClose, onCreated }: { onClose: () => void; onCreated: () => void }) {
  const [error, setError] = useState(""); const [busy, setBusy] = useState(false);
  return <div className="modal-backdrop" onClick={onClose}><FAQCreateForm onClose={onClose} onCreated={onCreated} error={error} setError={setError} busy={busy} setBusy={setBusy} /></div>;
}

function FAQCreateForm({ onClose, onCreated, error, setError, busy, setBusy }: { onClose: () => void; onCreated: () => void; error: string; setError: (value: string) => void; busy: boolean; setBusy: (value: boolean) => void }) {
  const [question, setQuestion] = useState(""); const [answer, setAnswer] = useState(""); const [category, setCategory] = useState("Chung");
  async function submit(event: React.FormEvent) {
    event.preventDefault(); setBusy(true); setError("");
    try { await api("/admin/faqs", { method: "POST", body: JSON.stringify({ question, answer, category }) }); onCreated(); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Không tạo được FAQ."); }
    finally { setBusy(false); }
  }
  return <section className="form-modal" role="dialog" aria-modal="true" onClick={event => event.stopPropagation()}><div className="modal-heading"><div><div className="eyebrow">KHO TRI THỨC</div><h2>Thêm câu hỏi thường gặp</h2></div><button className="modal-close" onClick={onClose}>×</button></div><form className="form-stack" onSubmit={submit}><label>Câu hỏi<input required minLength={6} value={question} onChange={event => setQuestion(event.target.value)} /></label><label>Trả lời<textarea required minLength={8} rows={5} value={answer} onChange={event => setAnswer(event.target.value)} /></label><label>Chủ đề<input value={category} onChange={event => setCategory(event.target.value)} /></label>{error && <ErrorNotice message={error} />}<div className="modal-actions"><button type="button" className="button button-ghost" onClick={onClose}>Hủy</button><button className="button button-primary" disabled={busy}>{busy ? "Đang lưu…" : "Lưu FAQ"}</button></div></form></section>;
}
