import { LoaderCircle } from "lucide-react";

export function PageTitle({ eyebrow, title, description, action }: { eyebrow?: string; title: string; description?: string; action?: React.ReactNode }) {
  return <div className="page-title-row"><div>{eyebrow && <div className="eyebrow">{eyebrow}</div>}<h1>{title}</h1>{description && <p>{description}</p>}</div>{action && <div className="title-action">{action}</div>}</div>;
}

export function Loading({ label = "Đang tải dữ liệu…" }: { label?: string }) {
  return <div className="loading"><LoaderCircle size={18} className="spin" /> {label}</div>;
}

export function EmptyState({ icon, title, description, action }: { icon?: React.ReactNode; title: string; description: string; action?: React.ReactNode }) {
  return <div className="empty-state"><div className="empty-icon">{icon}</div><strong>{title}</strong><p>{description}</p>{action}</div>;
}

export function StatusBadge({ children }: { children: React.ReactNode }) {
  const label = String(children);
  const tone = /Đã nghỉ việc|Đã đóng|Không|Bảo lưu/i.test(label) ? "muted" : /Tạm nghỉ|Cần|Chờ|Mới|Xét/i.test(label) ? "warning" : /Đã giải quyết|Đã tốt nghiệp|Trúng|Đang học|Đang công tác|Mở/i.test(label) ? "success" : "info";
  return <span className={`status-badge ${tone}`}><i />{children}</span>;
}

export function ErrorNotice({ message }: { message: string }) {
  return <div className="error-notice" role="alert">{message}</div>;
}
