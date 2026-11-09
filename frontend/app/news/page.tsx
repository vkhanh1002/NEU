"use client";

import Link from "next/link";
import { FormEvent, useCallback, useEffect, useState } from "react";
import { ArrowLeft, ArrowRight, Bot, CalendarDays, ExternalLink, Search } from "lucide-react";
import { EmptyState, ErrorNotice, Loading } from "@/components/ui";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";

type Article = { slug: string; title: string; category: string; summary: string; image_url: string; source_url: string; published_at: string | null };
type NewsPayload = { items: Article[]; categories: string[]; page: number; pages: number; total: number };
type EventItem = { id: string; title: string; category: string; summary: string; location: string; starts_at: string; ends_at: string; is_all_day: boolean; source_url: string };
type EventState = "upcoming" | "ongoing" | "past" | "all";
const eventStateLabels: Record<EventState, string> = { upcoming: "Sắp diễn ra", ongoing: "Đang diễn ra", past: "Đã diễn ra", all: "Tất cả" };

export default function NewsPage() {
  const { user } = useAuth();
  const [data, setData] = useState<NewsPayload | null>(null); const [events, setEvents] = useState<EventItem[]>([]);
  const [view, setView] = useState<"news" | "events">("news"); const [eventState, setEventState] = useState<EventState>("upcoming"); const [month, setMonth] = useState("");
  const [query, setQuery] = useState(""); const [submittedQuery, setSubmittedQuery] = useState(""); const [category, setCategory] = useState(""); const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true); const [error, setError] = useState("");
  const load = useCallback(async () => {
    setLoading(true); setError("");
    try {
      const params = new URLSearchParams({ page: String(page), page_size: "9" });
      if (submittedQuery) params.set("q", submittedQuery); if (category) params.set("category", category);
      const eventParams = new URLSearchParams({ state: view === "events" ? eventState : "upcoming" });
      if (month && view === "events") eventParams.set("month", month);
      const [news, eventData] = await Promise.all([api<NewsPayload>(`/news?${params}`), api<{ items: EventItem[] }>(`/news/events/list?${eventParams}`)]);
      setData(news); setEvents(eventData.items);
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Không tải được nội dung."); }
    finally { setLoading(false); }
  }, [category, page, submittedQuery, eventState, month, view]);
  useEffect(() => { void load(); }, [load]);
  function search(event: FormEvent) { event.preventDefault(); setPage(1); setSubmittedQuery(query.trim()); }
  const nextEvent = events.find(item => new Date(item.starts_at).getTime() > Date.now());

  return <main className="news-page">
    <section className="news-hero"><div><span className="neu-section-label">CỔNG THÔNG TIN NEU · CẬP NHẬT NGUỒN CHÍNH THỨC</span><h1>Tin tức và sự kiện</h1><p>Tin hoạt động học thuật, đào tạo, nghiên cứu và lịch sự kiện của Đại học Kinh tế Quốc dân.</p></div><div className="news-hero-mark"><CalendarDays size={42} /></div></section>
    <section className="news-assistant-callout"><div className="news-assistant-icon"><Bot size={20} /></div><div><strong>Cần tìm hiểu thêm về tuyển sinh?</strong><p>Đặt câu hỏi cho trợ lý để tra cứu thông tin có nguồn tham khảo.</p></div>{user ? <Link href="/assistant">Trò chuyện <ArrowRight size={15} /></Link> : <button onClick={() => window.dispatchEvent(new Event("neu:open-assistant"))}>Trò chuyện <ArrowRight size={15} /></button>}</section>
    <div className="news-main-tabs" role="tablist" aria-label="Nội dung NEU"><button role="tab" aria-selected={view === "news"} className={view === "news" ? "active" : ""} onClick={() => setView("news")}>Tin tức <span>{data?.total ?? ""}</span></button><button role="tab" aria-selected={view === "events"} className={view === "events" ? "active" : ""} onClick={() => setView("events")}>Sự kiện <CalendarDays size={16} /></button></div>
    {error && <ErrorNotice message={error} />}
    {view === "news" ? <section className="news-content news-full-content"><div className="news-tools"><div><span className="neu-section-label">BẢN TIN NEU</span><h2>Tin mới nhất</h2></div><form onSubmit={search} className="news-search"><Search size={16} /><input value={query} onChange={event => setQuery(event.target.value)} placeholder="Tìm tin tức…" aria-label="Tìm tin tức" /><button aria-label="Tìm kiếm"><ArrowRight size={15} /></button></form></div>
      <div className="news-categories"><button className={!category ? "active" : ""} onClick={() => { setPage(1); setCategory(""); }}>Tất cả</button>{(data?.categories ?? []).map(value => <button key={value} className={category === value ? "active" : ""} onClick={() => { setPage(1); setCategory(value); }}>{value}</button>)}</div>
      {nextEvent && <a className="news-next-event" href={nextEvent.source_url || "/news"} target="_blank" rel="noreferrer"><span className="news-next-event-date"><small>SẮP DIỄN RA</small><strong>{formatDate(nextEvent.starts_at)}</strong></span><span className="news-next-event-copy"><small>{nextEvent.category} · {nextEvent.is_all_day ? "Cả ngày" : `${formatTime(nextEvent.starts_at)}–${formatTime(nextEvent.ends_at)}`}</small><strong>{nextEvent.title}</strong><span>{nextEvent.summary}</span></span><ArrowRight size={19} /></a>}
      {loading ? <Loading label="Đang tải tin tức…" /> : data?.items.length ? <>
        <div className="news-card-grid">{data.items.map((article, index) => <Link className={`news-card ${index === 0 && page === 1 && !category && !submittedQuery ? "featured" : ""}`} href={`/news/${article.slug}`} key={article.slug}><div className="news-card-image" style={{ backgroundImage: article.image_url ? `url("${article.image_url}")` : "linear-gradient(135deg,#dceaf5,#aac7dd)" }}><span>{article.category}</span></div><div className="news-card-copy"><time>{article.published_at ? formatDate(article.published_at) : ""}</time><h3>{article.title}</h3><p>{article.summary}</p><b>Đọc tiếp <ArrowRight size={14} /></b></div></Link>)}</div>
        {data.pages > 1 && <nav className="news-pagination" aria-label="Phân trang">{page > 1 && <button onClick={() => setPage(page - 1)}><ArrowLeft size={15} /> Trước</button>}<span>Trang {page} / {data.pages} · {data.total} bài viết</span>{page < data.pages && <button onClick={() => setPage(page + 1)}>Tiếp <ArrowRight size={15} /></button>}</nav>}
      </> : <EmptyState title="Không có bài viết phù hợp" description="Thử đổi từ khóa hoặc chọn danh mục khác." />}</section> : <section className="news-events-page"><div className="news-tools"><div><span className="neu-section-label">LỊCH SỰ KIỆN</span><h2>{eventStateLabels[eventState]}</h2></div><label className="news-month-filter">Theo tháng<input type="month" value={month} onChange={event => setMonth(event.target.value)} /></label></div>
      <div className="news-categories event-state-tabs">{(["upcoming", "ongoing", "past", "all"] as EventState[]).map(value => <button key={value} className={eventState === value ? "active" : ""} onClick={() => setEventState(value)}>{eventStateLabels[value]}</button>)}</div>
      {loading ? <Loading label="Đang tải lịch sự kiện…" /> : events.length ? <div className="event-card-list">{events.map(item => <article className="event-card" key={item.id}><div className="event-card-date"><strong>{dateParts(item.starts_at).day}</strong><span>{dateParts(item.starts_at).monthYear}</span></div><div className="event-card-copy"><span className="event-card-category">{item.category} · {eventStateLabels[eventState]}</span><h3>{item.title}</h3><p>{item.summary}</p><div className="event-card-meta"><span><CalendarDays size={14} />{item.is_all_day ? "Cả ngày" : `${formatDateTime(item.starts_at)} – ${formatTime(item.ends_at)}`}</span>{item.location && <span>{item.location}</span>}</div></div>{item.source_url && <a className="event-source-button" href={item.source_url} target="_blank" rel="noreferrer">Nguồn NEU <ExternalLink size={14} /></a>}</article>)}</div> : <EmptyState icon={<CalendarDays size={22} />} title={eventState === "upcoming" ? "Chưa có sự kiện sắp diễn ra" : "Không có sự kiện trong bộ lọc này"} description="Sự kiện hiển thị khi đã được quản trị viên xác nhận và gắn nguồn chính thức." />}</section>}
    <div className="news-back-home"><Link href="/"><ArrowLeft size={15} /> Về trang giới thiệu</Link></div>
  </main>;
}

function formatDate(value: string) { return new Date(value).toLocaleDateString("vi-VN", { timeZone: "Asia/Ho_Chi_Minh", day: "numeric", month: "long", year: "numeric" }); }
function formatDateTime(value: string) { return new Date(value).toLocaleString("vi-VN", { timeZone: "Asia/Ho_Chi_Minh", day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" }); }
function formatTime(value: string) { return new Date(value).toLocaleTimeString("vi-VN", { timeZone: "Asia/Ho_Chi_Minh", hour: "2-digit", minute: "2-digit" }); }
function dateParts(value: string) { const date = new Date(value); return { day: date.toLocaleDateString("vi-VN", { timeZone: "Asia/Ho_Chi_Minh", day: "2-digit" }), monthYear: date.toLocaleDateString("vi-VN", { timeZone: "Asia/Ho_Chi_Minh", month: "short", year: "numeric" }) }; }
