"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { Bell, CheckCheck, CircleHelp } from "lucide-react";
import { EmptyState, ErrorNotice, Loading, PageTitle } from "@/components/ui";
import { api } from "@/lib/api";

type Notice = { id: string; title: string; message: string; href: string; created_at: string; read_at: string | null };
type NoticePayload = { items: Notice[]; unread_count: number };
export function NotificationsPage() {
  const [data, setData] = useState<NoticePayload | null>(null); const [error, setError] = useState(""); const [loading, setLoading] = useState(true);
  const load = useCallback(async () => { setLoading(true); setError(""); try { setData(await api<NoticePayload>("/notifications")); } catch (reason) { setError(reason instanceof Error ? reason.message : "Không tải được thông báo."); } finally { setLoading(false); } }, []);
  useEffect(() => { void load(); }, [load]);
  async function markRead(item: Notice) { if (item.read_at) return; try { await api(`/notifications/${item.id}/read`, { method: "PATCH" }); setData(current => current ? { ...current, unread_count: Math.max(0, current.unread_count - 1), items: current.items.map(row => row.id === item.id ? { ...row, read_at: new Date().toISOString() } : row) } : current); } catch (reason) { setError(reason instanceof Error ? reason.message : "Không cập nhật được thông báo."); } }
  return <div className="module-page"><PageTitle eyebrow="DỊCH VỤ SINH VIÊN" title="Thông báo" description="Thông báo được gửi đến tài khoản của bạn." action={<span className="notification-count">{data?.unread_count ?? 0} chưa đọc</span>} />{error && <ErrorNotice message={error} />}{loading ? <Loading /> : data?.items.length ? <div className="student-notification-page">{data.items.map(item => <article className={`student-notification-card ${item.read_at ? "" : "unread"}`} key={item.id}><div className="notification-card-icon"><Bell size={17} /></div><div className="notification-card-copy"><strong>{item.title}</strong><p>{item.message}</p><time>{new Date(item.created_at).toLocaleString("vi-VN", { dateStyle: "medium", timeStyle: "short" })}</time></div><div className="notification-card-actions">{!item.read_at && <button className="button button-secondary" onClick={() => void markRead(item)}><CheckCheck size={15} /> Đánh dấu đã đọc</button>}<Link className="button button-ghost" href={item.href} onClick={() => void markRead(item)}>Mở mục liên quan</Link></div></article>)}</div> : <EmptyState icon={<CircleHelp size={22} />} title="Chưa có thông báo" description="Các cập nhật quan trọng sẽ được gửi đến đây." />}</div>;
}
