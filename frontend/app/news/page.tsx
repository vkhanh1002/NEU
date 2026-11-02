"use client";

import Link from "next/link";
import { FormEvent, useCallback, useEffect, useState } from "react";
import { ArrowLeft, ArrowRight, Bot, CalendarDays, Search } from "lucide-react";
import { EmptyState, ErrorNotice, Loading } from "@/components/ui";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";

type Article = { slug: string; title: string; category: string; summary: string; image_url: string; published_at: string | null };
type NewsPayload = { items: Article[]; categories: string[]; page: number; pages: number; total: number };
type EventItem = { id: string; title: string; category: string; summary: string; location: string; starts_at: string; ends_at: string };
export default function NewsPage() {
  const { user } = useAuth();
  const [data, setData] = useState<NewsPayload | null>(null); const [events, setEvents] = useState<EventItem[]>([]);
  const [query, setQuery] = useState(""); const [submittedQuery, setSubmittedQuery] = useState(""); const [category, setCategory] = useState(""); const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true); const [error, setError] = useState("");
  const load = useCallback(async () => {
    setLoading(true); setError("");
    try {
      const params = new URLSearchParams({ page: String(page), page_size: "9" });
      if (submittedQuery) params.set("q", submittedQuery); if (category) params.set("category", category);
      const [news, eventData] = await Promise.all([api<NewsPayload>(`/news?${params}`), api<{ items: EventItem[] }>("/news/events/upcoming")]);
      setData(news); setEvents(eventData.items);
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Không tải được tin tức."); }
    finally { setLoading(false); }
  }, [category, page, submittedQuery]);
  useEffect(() => { void load(); }, [load]);
  function search(event: FormEvent) { event.preventDefault(); setPage(1); setSubmittedQuery(query.trim()); }
  return <main className="news-page">
    <section className="news-hero"><div><span className="neu-section-label">CỔNG THÔNG TIN NEU</span><h1>Tin tức và sự kiện</h1><p>Cập nhật hoạt động học thuật, hướng dẫn người học và thông tin tuyển sinh.</p></div><div className="news-hero-mark"><CalendarDays size={42} /></div></section>
    <section className="news-assistant-callout"><div className="news-assistant-icon"><Bot size={20} /></div><div><strong>Cần tìm hiểu thêm về tuyển sinh?</strong><p>Đặt câu hỏi cho trợ lý để tra cứu thông tin có nguồn tham khảo.</p></div>{user ? <Link href="/assistant">Trò chuyện <ArrowRight size={15} /></Link> : <button onClick={() => window.dispatchEvent(new Event("neu:open-assistant"))}>Trò chuyện <ArrowRight size={15} /></button>}</section>
    <div className="news-layout"><section className="news-content"><div className="news-tools"><div><span className="neu-section-label">CẬP NHẬT</span><h2>Tin mới nhất</h2></div><form onSubmit={search} className="news-search"><Search size={16} /><input value={query} onChange={event => setQuery(event.target.value)} placeholder="Tìm tin tức…" aria-label="Tìm tin tức" /><button aria-label="Tìm kiếm"><ArrowRight size={15} /></button></form></div>
      <div className="news-categories"><button className={!category ? "active" : ""} onClick={() => { setPage(1); setCategory(""); }}>Tất cả</button>{(data?.categories ?? []).map(value => <button key={value} className={category === value ? "active" : ""} onClick={() => { setPage(1); setCategory(value); }}>{value}</button>)}</div>
      {error && <ErrorNotice message={error} />}{loading ? <Loading label="Đang tải tin tức…" /> : data?.items.length ? <>
        <div className="news-card-grid">{data.items.map((article, index) => <Link className={`news-card ${index === 0 && page === 1 && !category && !submittedQuery ? "featured" : ""}`} href={`/news/${article.slug}`} key={article.slug}><div className="news-card-image" style={{ backgroundImage: `url("${article.image_url}")` }}><span>{article.category}</span></div><div className="news-card-copy"><time>{article.published_at ? new Date(article.published_at).toLocaleDateString("vi-VN") : ""}</time><h3>{article.title}</h3><p>{article.summary}</p><b>Đọc tiếp <ArrowRight size={14} /></b></div></Link>)}</div>
        {data.pages > 1 && <nav className="news-pagination" aria-label="Phân trang">{page > 1 && <button onClick={() => setPage(page - 1)}><ArrowLeft size={15} /> Trước</button>}<span>Trang {page} / {data.pages} · {data.total} bài viết</span>{page < data.pages && <button onClick={() => setPage(page + 1)}>Tiếp <ArrowRight size={15} /></button>}</nav>}
      </> : <EmptyState title="Không có bài viết phù hợp" description="Thử đổi từ khóa hoặc chọn danh mục khác." />}
    </section>
    <aside className="news-events"><span className="neu-section-label">LỊCH SỰ KIỆN</span><h2>Sắp diễn ra</h2>{events.length ? events.map(event => <article key={event.id}><time>{new Date(event.starts_at).toLocaleDateString("vi-VN", { day: "numeric", month: "short" })}</time><div><small>{event.category}</small><strong>{event.title}</strong><p>{event.summary}</p><span>{event.location}</span></div></article>) : <div className="news-events-empty"><CalendarDays size={20} /><strong>Chưa có sự kiện được công bố</strong><span>Lịch sự kiện sẽ hiển thị sau khi được đơn vị phụ trách xác nhận.</span></div>}</aside></div>
    <div className="news-back-home"><Link href="/"><ArrowLeft size={15} /> Về trang giới thiệu</Link></div>
  </main>;
}
