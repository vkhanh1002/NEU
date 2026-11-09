"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { CalendarDays, Check, ExternalLink, FileText, Pencil, Plus, RefreshCw, Search, Trash2 } from "lucide-react";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { EmptyState, ErrorNotice, Loading, PageTitle, StatusBadge } from "@/components/ui";

type NewsRow = { id: string; slug: string; title: string; category: string; summary: string; content: string; image_url: string; source_url: string; published_at: string | null; status: string };
type EventRow = { id: string; title: string; category: string; summary: string; location: string; starts_at: string; ends_at: string; is_all_day: boolean; source_url: string; status: string };
type Section = "news" | "events";

export function ContentAdmin() {
  const { user } = useAuth();
  const [section, setSection] = useState<Section>("news");
  const [news, setNews] = useState<NewsRow[]>([]);
  const [events, setEvents] = useState<EventRow[]>([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [editingNews, setEditingNews] = useState<NewsRow | null | undefined>(undefined);
  const [editingEvent, setEditingEvent] = useState<EventRow | null | undefined>(undefined);
  const isAdmin = user?.role === "super_admin";

  const load = useCallback(async () => {
    setError("");
    try {
      const [articles, schedule] = await Promise.all([
        api<NewsRow[]>("/admin/content/news"), api<EventRow[]>("/admin/content/events"),
      ]);
      setNews(articles); setEvents(schedule);
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Không tải được tin tức và sự kiện."); }
    finally { setLoading(false); }
  }, []);
  useEffect(() => { if (isAdmin) void load(); else setLoading(false); }, [isAdmin, load]);

  const filteredNews = useMemo(() => news.filter(row => `${row.title} ${row.category} ${row.status}`.toLowerCase().includes(query.toLowerCase())), [news, query]);
  const filteredEvents = useMemo(() => events.filter(row => `${row.title} ${row.category} ${row.status}`.toLowerCase().includes(query.toLowerCase())), [events, query]);

  async function remove(kind: Section, row: NewsRow | EventRow) {
    if (!window.confirm(`Xóa ${kind === "news" ? "bài viết" : "sự kiện"} “${row.title}”?`)) return;
    try {
      await api(`/admin/content/${kind}/${row.id}`, { method: "DELETE" });
      if (kind === "news") setNews(current => current.filter(item => item.id !== row.id));
      else setEvents(current => current.filter(item => item.id !== row.id));
      setNotice("Đã xóa nội dung.");
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Không xóa được nội dung."); }
  }

  if (!user || !isAdmin) return <div className="module-page"><PageTitle eyebrow="QUẢN TRỊ" title="Tin tức và sự kiện" description="Biên tập nội dung công khai của cổng NEU." /><EmptyState title={user ? "Không đủ quyền truy cập" : "Đăng nhập với quyền quản trị"} description="Chỉ quản trị viên mới có thể quản lý nội dung. API cũng kiểm tra quyền trên mọi thao tác." /></div>;

  return <div className="module-page content-admin-page">
    <PageTitle eyebrow="QUẢN TRỊ NỘI DUNG" title="Tin tức và sự kiện" description="Duyệt nội dung, ngày đăng và nguồn tham khảo trước khi xuất bản." action={<button className="button button-secondary" onClick={() => void load()}><RefreshCw size={15} /> Làm mới</button>} />
    <div className="module-notice"><FileText size={16} /><span>Nội dung công khai cần có liên kết HTTPS đến nguồn xác minh. Bài viết cần ngày đăng; sự kiện cần khung thời gian hợp lệ. Địa điểm có thể để trống khi nguồn chưa công bố.</span></div>
    {error && <ErrorNotice message={error} />}{notice && <div className="success-notice"><Check size={16} />{notice}</div>}
    <div className="module-toolbar content-admin-toolbar">
      <div className="tab-switch"><button className={section === "news" ? "selected" : ""} onClick={() => { setSection("news"); setQuery(""); }}>Tin tức <span>{news.length}</span></button><button className={section === "events" ? "selected" : ""} onClick={() => { setSection("events"); setQuery(""); }}>Sự kiện <span>{events.length}</span></button></div>
      <div className="search-field"><Search size={16} /><input value={query} onChange={event => setQuery(event.target.value)} placeholder="Tìm tiêu đề, danh mục…" /></div>
      <button className="button button-primary" onClick={() => section === "news" ? setEditingNews(null) : setEditingEvent(null)}><Plus size={16} /> Thêm {section === "news" ? "bài viết" : "sự kiện"}</button>
    </div>
    {loading ? <Loading /> : section === "news" ? filteredNews.length ? <div className="table-panel"><div className="responsive-table"><table><thead><tr><th>Bài viết</th><th>Danh mục</th><th>Ngày đăng</th><th>Nguồn</th><th>Trạng thái</th><th>Thao tác</th></tr></thead><tbody>{filteredNews.map(row => <tr key={row.id}><td><strong>{row.title}</strong><small>/{row.slug}</small></td><td>{row.category}</td><td>{row.published_at ? formatDate(row.published_at) : "Chưa đặt"}</td><td>{row.source_url ? <a className="content-source-link" href={row.source_url} target="_blank" rel="noreferrer">Mở nguồn <ExternalLink size={13} /></a> : "Chưa có"}</td><td><StatusBadge>{statusLabel(row.status)}</StatusBadge></td><td><div className="row-actions"><button className="mini-button" onClick={() => setEditingNews(row)}><Pencil size={14} /> Sửa</button><button className="icon-button subtle-danger" onClick={() => void remove("news", row)} aria-label="Xóa bài viết"><Trash2 size={15} /></button></div></td></tr>)}</tbody></table></div></div> : <EmptyState icon={<FileText size={22} />} title="Chưa có bài viết phù hợp" description="Thêm bài viết có nguồn để xuất bản nội dung đã xác minh." /> : filteredEvents.length ? <div className="table-panel"><div className="responsive-table"><table><thead><tr><th>Sự kiện</th><th>Thời gian</th><th>Địa điểm</th><th>Nguồn</th><th>Trạng thái</th><th>Thao tác</th></tr></thead><tbody>{filteredEvents.map(row => <tr key={row.id}><td><strong>{row.title}</strong><small>{row.category} · {row.is_all_day ? "Cả ngày" : "Theo giờ"}</small></td><td>{formatDate(row.starts_at)}{!row.is_all_day && ` · ${formatTime(row.starts_at)}–${formatTime(row.ends_at)}`}</td><td>{row.location || "Chưa công bố"}</td><td>{row.source_url ? <a className="content-source-link" href={row.source_url} target="_blank" rel="noreferrer">Mở nguồn <ExternalLink size={13} /></a> : "Chưa có"}</td><td><StatusBadge>{statusLabel(row.status)}</StatusBadge></td><td><div className="row-actions"><button className="mini-button" onClick={() => setEditingEvent(row)}><Pencil size={14} /> Sửa</button><button className="icon-button subtle-danger" onClick={() => void remove("events", row)} aria-label="Xóa sự kiện"><Trash2 size={15} /></button></div></td></tr>)}</tbody></table></div></div> : <EmptyState icon={<CalendarDays size={22} />} title="Chưa có sự kiện phù hợp" description="Thêm sự kiện đã được xác nhận và ghi rõ nguồn tham khảo." />}
    {editingNews !== undefined && <ContentDialog kind="news" initial={editingNews} onClose={() => setEditingNews(undefined)} onSaved={async () => { setEditingNews(undefined); setNotice("Đã lưu bài viết."); await load(); }} />}
    {editingEvent !== undefined && <ContentDialog kind="events" initial={editingEvent} onClose={() => setEditingEvent(undefined)} onSaved={async () => { setEditingEvent(undefined); setNotice("Đã lưu sự kiện."); await load(); }} />}
  </div>;
}

function ContentDialog({ kind, initial, onClose, onSaved }: { kind: Section; initial: NewsRow | EventRow | null; onClose: () => void; onSaved: () => void }) {
  const news = kind === "news" ? initial as NewsRow | null : null;
  const event = kind === "events" ? initial as EventRow | null : null;
  const [busy, setBusy] = useState(false); const [error, setError] = useState("");
  const [status, setStatus] = useState(initial?.status ?? "draft");
  const [title, setTitle] = useState(initial?.title ?? ""); const [category, setCategory] = useState(initial?.category ?? (kind === "news" ? "70 năm NEU" : "70 năm NEU"));
  const [summary, setSummary] = useState(initial?.summary ?? ""); const [sourceUrl, setSourceUrl] = useState(initial?.source_url ?? "");
  const [slug, setSlug] = useState(news?.slug ?? ""); const [content, setContent] = useState(news?.content ?? "");
  const [imageUrl, setImageUrl] = useState(news?.image_url ?? ""); const [publishedAt, setPublishedAt] = useState(toInputDateTime(news?.published_at ?? null));
  const [location, setLocation] = useState(event?.location ?? ""); const [startsAt, setStartsAt] = useState(toInputDateTime(event?.starts_at ?? null)); const [endsAt, setEndsAt] = useState(toInputDateTime(event?.ends_at ?? null)); const [allDay, setAllDay] = useState(event?.is_all_day ?? false);
  const endpoint = `/admin/content/${kind}${initial ? `/${initial.id}` : ""}`;
  async function submit(form: React.FormEvent) {
    form.preventDefault(); setBusy(true); setError("");
    const body = kind === "news"
      ? { slug: slug.trim(), title: title.trim(), category: category.trim(), summary: summary.trim(), content: content.trim(), image_url: imageUrl.trim(), source_url: sourceUrl.trim(), published_at: publishedAt ? new Date(publishedAt).toISOString() : null, status }
      : { title: title.trim(), category: category.trim(), summary: summary.trim(), location: location.trim(), starts_at: startsAt ? new Date(startsAt).toISOString() : "", ends_at: endsAt ? new Date(endsAt).toISOString() : "", is_all_day: allDay, source_url: sourceUrl.trim(), status };
    try { await api(endpoint, { method: initial ? "PATCH" : "POST", body: JSON.stringify(body) }); onSaved(); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Không lưu được nội dung."); }
    finally { setBusy(false); }
  }
  return <div className="modal-backdrop" onClick={onClose}><section className="form-modal content-editor-modal" role="dialog" aria-modal="true" onClick={event => event.stopPropagation()}><div className="modal-heading"><div><div className="eyebrow">{kind === "news" ? "TIN TỨC" : "SỰ KIỆN"}</div><h2>{initial ? "Chỉnh sửa nội dung" : "Thêm nội dung"}</h2><p>Kiểm tra thông tin nguồn và trạng thái trước khi lưu.</p></div><button className="modal-close" onClick={onClose} aria-label="Đóng">×</button></div>
    <form className="form-stack" onSubmit={submit}><label>Tiêu đề<input required minLength={8} maxLength={200} value={title} onChange={event => setTitle(event.target.value)} /></label><div className="form-row"><label>Danh mục<input required value={category} onChange={event => setCategory(event.target.value)} /></label><label>Trạng thái<select value={status} onChange={event => setStatus(event.target.value)}><option value="draft">Bản nháp</option><option value="published">Công khai</option><option value="archived">Lưu trữ</option></select></label></div><label>Mô tả ngắn<textarea required minLength={15} maxLength={600} rows={3} value={summary} onChange={event => setSummary(event.target.value)} /></label>
      {kind === "news" ? <><label>Đường dẫn (slug)<input required pattern="[a-z0-9]+(-[a-z0-9]+)*" value={slug} onChange={event => setSlug(event.target.value)} placeholder="khoa-thong-ke-70-nam" /></label><label>Nội dung chi tiết<textarea required minLength={30} rows={6} value={content} onChange={event => setContent(event.target.value)} /></label><label>URL ảnh đại diện (HTTPS)<input type="url" value={imageUrl} onChange={event => setImageUrl(event.target.value)} placeholder="https://…" /></label><label>Ngày đăng<input type="datetime-local" value={publishedAt} onChange={event => setPublishedAt(event.target.value)} /></label></> : <><div className="form-row"><label>Bắt đầu<input required type="datetime-local" value={startsAt} onChange={event => setStartsAt(event.target.value)} /></label><label>Kết thúc<input required type="datetime-local" value={endsAt} onChange={event => setEndsAt(event.target.value)} /></label></div><label>Địa điểm (để trống nếu nguồn chưa công bố)<input value={location} onChange={event => setLocation(event.target.value)} /></label><label className="content-checkbox"><input type="checkbox" checked={allDay} onChange={event => setAllDay(event.target.checked)} /> Sự kiện cả ngày</label></>}
      <label>Nguồn tham khảo (HTTPS)<input type="url" required={status === "published"} value={sourceUrl} onChange={event => setSourceUrl(event.target.value)} placeholder="https://neu.edu.vn/…" /></label>
      {error && <ErrorNotice message={error} />}<div className="modal-actions"><button type="button" className="button button-ghost" onClick={onClose}>Hủy</button><button className="button button-primary" disabled={busy}>{busy ? "Đang lưu…" : "Lưu nội dung"}</button></div>
    </form></section></div>;
}

function statusLabel(value: string) { return value === "published" ? "Đang công khai" : value === "archived" ? "Đã lưu trữ" : "Bản nháp"; }
function toInputDateTime(value: string | null) { if (!value) return ""; const date = new Date(value); const local = new Date(date.getTime() - date.getTimezoneOffset() * 60000); return local.toISOString().slice(0, 16); }
function formatDate(value: string) { return new Date(value).toLocaleDateString("vi-VN", { timeZone: "Asia/Ho_Chi_Minh", dateStyle: "medium" }); }
function formatTime(value: string) { return new Date(value).toLocaleTimeString("vi-VN", { timeZone: "Asia/Ho_Chi_Minh", hour: "2-digit", minute: "2-digit" }); }
