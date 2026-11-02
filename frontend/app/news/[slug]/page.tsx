"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { ArrowLeft, ArrowRight } from "lucide-react";
import { EmptyState, ErrorNotice, Loading } from "@/components/ui";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";

type Article = { slug: string; title: string; category: string; summary: string; content: string; image_url: string; published_at: string | null };
export default function NewsDetailPage() {
  const { user } = useAuth();
  const params = useParams<{ slug: string }>(); const slug = params.slug;
  const [article, setArticle] = useState<Article | null>(null); const [loading, setLoading] = useState(true); const [error, setError] = useState("");
  useEffect(() => { let live = true; setLoading(true); api<Article>(`/news/${encodeURIComponent(slug)}`).then(value => { if (live) setArticle(value); }).catch(reason => { if (live) setError(reason instanceof Error ? reason.message : "Không tải được bài viết."); }).finally(() => { if (live) setLoading(false); }); return () => { live = false; }; }, [slug]);
  if (loading) return <div className="news-detail-page"><Loading label="Đang tải bài viết…" /></div>;
  if (error) return <div className="news-detail-page"><ErrorNotice message={error} /><EmptyState title="Không tìm thấy bài viết" description="Bài viết có thể đã được gỡ khỏi danh sách." action={<Link className="button button-secondary" href="/news">Quay lại tin tức</Link>} /></div>;
  if (!article) return <div className="news-detail-page"><EmptyState title="Không tìm thấy bài viết" description="Bài viết không còn khả dụng." /></div>;
  return <main className="news-detail-page"><Link className="news-back-link" href="/news"><ArrowLeft size={15} /> Tin tức và sự kiện</Link><article><div className="news-detail-cover" style={{ backgroundImage: `url("${article.image_url}")` }} /><div className="news-detail-copy"><span className="news-detail-category">{article.category}</span><time>{article.published_at ? new Date(article.published_at).toLocaleDateString("vi-VN", { dateStyle: "long" }) : ""}</time><h1>{article.title}</h1><p className="news-detail-summary">{article.summary}</p>{article.content.split(/\n\n+/).map((paragraph, index) => <p key={index}>{paragraph}</p>)}{user ? <Link className="button button-primary" href="/assistant">Hỏi trợ lý tư vấn <ArrowRight size={15} /></Link> : <button className="button button-primary" onClick={() => window.dispatchEvent(new Event("neu:open-assistant"))}>Hỏi trợ lý tư vấn <ArrowRight size={15} /></button>}</div></article></main>;
}
