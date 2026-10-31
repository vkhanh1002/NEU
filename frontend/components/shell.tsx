"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { Bot, Bell, BookOpen, CheckCheck, ChevronDown, ChevronLeft, ChevronRight, CircleHelp, GraduationCap, LayoutDashboard, LogIn, Menu, Search, UsersRound, BriefcaseBusiness, UserRound, ShieldCheck, X } from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { api } from "@/lib/api";

type NavigationLink = { label: string; href: string; icon: typeof LayoutDashboard; roles?: string[] };
const navigation: { title: string; links: NavigationLink[] }[] = [
  { title: "TỔNG QUAN", links: [{ label: "Dashboard", href: "/", icon: LayoutDashboard }] },
  { title: "TUYỂN SINH", links: [{ label: "Tuyển sinh & hồ sơ xét tuyển", href: "/admissions", icon: GraduationCap, roles: ["super_admin", "admission_staff"] }] },
  { title: "QUẢN LÝ HỒ SƠ", links: [
    { label: "Hồ sơ sinh viên", href: "/profiles", icon: UsersRound, roles: ["super_admin", "student"] },
    { label: "Hồ sơ giảng viên", href: "/personnel/lecturers", icon: GraduationCap, roles: ["super_admin"] },
    { label: "Hồ sơ nhân viên", href: "/personnel/employees", icon: BriefcaseBusiness, roles: ["super_admin"] },
  ] },
  { title: "HỖ TRỢ NGƯỜI HỌC", links: [
    { label: "Trung tâm hỗ trợ", href: "/support", icon: CircleHelp },
    { label: "Quản lý FAQ", href: "/admin", icon: BookOpen, roles: ["super_admin"] },
  ] },
  { title: "AI ASSISTANT", links: [
    { label: "Trợ lý Study AI", href: "/assistant", icon: Bot },
    { label: "Kho tri thức AI", href: "/admin", icon: BookOpen, roles: ["super_admin"] },
  ] },
  { title: "NHÂN SỰ", links: [{ label: "Tổng quan nhân sự", href: "/personnel", icon: UserRound, roles: ["super_admin"] }] },
];

export function Shell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout } = useAuth();
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [loginOpen, setLoginOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [accountOpen, setAccountOpen] = useState(false);
  const [notificationOpen, setNotificationOpen] = useState(false);
  const [notifications, setNotifications] = useState<{ id: string; title: string; message: string; href: string; read_at: string | null; created_at: string }[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const visibleNavigation = navigation.map(group => ({ ...group, links: group.links.filter(link => !link.roles || link.roles.includes(user?.role ?? "")).map(link => link.href === "/support" && ["super_admin", "support_staff"].includes(user?.role ?? "") ? { ...link, label: "Danh sách yêu cầu" } : link) })).filter(group => group.links.length > 0);
  useEffect(() => {
    if (!user) { setNotifications([]); setUnreadCount(0); return; }
    let live = true;
    const refresh = () => api<{ items: typeof notifications; unread_count: number }>("/notifications").then(result => {
      if (live) { setNotifications(result.items); setUnreadCount(result.unread_count); }
    }).catch(() => {});
    void refresh();
    const timer = window.setInterval(() => { void refresh(); }, 30_000);
    return () => { live = false; window.clearInterval(timer); };
  }, [user?.id]);
  const title = navigation.flatMap(group => group.links).find(link => link.href === pathname)?.label ?? "Study";
  const search = (event: React.FormEvent) => {
    event.preventDefault();
    if (!query.trim()) return;
    router.push(`/admissions?search=${encodeURIComponent(query.trim())}`);
  };

  return <div className={`app-shell ${collapsed ? "sidebar-collapsed" : ""}`}>
    {mobileOpen && <button className="mobile-scrim" onClick={() => setMobileOpen(false)} aria-label="Đóng menu" />}
    <aside className={`sidebar ${mobileOpen ? "mobile-open" : ""}`}>
      <div className="sidebar-brand-row"><Link href="/" className="brand" onClick={() => setMobileOpen(false)}>
        <div className="brand-mark"><GraduationCap size={21} strokeWidth={2.3} /></div>
        <div className="brand-name"><strong>study<span>.</span></strong><small>UNIVERSITY PLATFORM</small></div>
      </Link><button className="mobile-close" onClick={() => setMobileOpen(false)} aria-label="Đóng"><X size={18} /></button></div>
      <div className="workspace-picker"><div className="campus-avatar">S</div><div className="workspace-name"><strong>Study University</strong><small>Workspace · Demo</small></div><ChevronDown size={15} /></div>
      <nav className="side-nav">
        {visibleNavigation.map(group => <div className="nav-group" key={group.title}>
          <div className="nav-group-title">{group.title}</div>
          {group.links.map(item => <Link href={item.href} key={item.href} onClick={() => setMobileOpen(false)} title={collapsed ? item.label : undefined}
            className={`nav-link ${pathname === item.href ? "active" : ""}`}><item.icon size={18} strokeWidth={1.8} /><span>{item.label}</span>{item.href === "/assistant" && <span className="nav-new">AI</span>}</Link>)}
        </div>)}
      </nav>
      <div className="sidebar-bottom">
        <div className="sidebar-help"><div className="help-orb"><Bot size={17} /></div><strong>Study AI sẵn sàng</strong><p>Hỏi đáp từ kho tri thức của trường.</p><Link href="/assistant" onClick={() => setMobileOpen(false)}>Bắt đầu trò chuyện <ChevronRight size={14} /></Link></div>
        <button className="collapse-button" onClick={() => setCollapsed(!collapsed)}><ChevronLeft className="collapse-icon" size={17} /><span>Thu gọn menu</span></button>
        <div className="sidebar-foot"><span className="online-dot" />Hệ thống hoạt động <span className="version">v1.0.0</span></div>
      </div>
    </aside>
    <main className="main-column">
      <header className="topbar">
        <div className="topbar-left"><button className="mobile-menu" onClick={() => setMobileOpen(true)} aria-label="Mở menu"><Menu size={21} /></button><div className="breadcrumbs"><span>Study</span><span>/</span><strong>{title}</strong></div></div>
        <div className="topbar-actions">
          <form className="global-search" onSubmit={search}><Search size={16} /><input value={query} onChange={event => setQuery(event.target.value)} placeholder="Tìm nhanh ngành, hồ sơ…" aria-label="Tìm kiếm" /><kbd>⌘ K</kbd></form>
          <div className="notification-wrap"><button className="icon-button notification-button" title="Thông báo" onClick={() => { setNotificationOpen(!notificationOpen); setAccountOpen(false); }}><Bell size={18} />{unreadCount > 0 && <i />}</button>{notificationOpen && <div className="notification-menu"><div className="notification-heading"><strong>Thông báo</strong><span>{unreadCount ? `${unreadCount} chưa đọc` : "Đã cập nhật"}</span></div>{notifications.length ? notifications.slice(0, 8).map(notification => <button className={`notification-item ${notification.read_at ? "" : "unread"}`} key={notification.id} onClick={async () => { if (!notification.read_at) { await api(`/notifications/${notification.id}/read`, { method: "PATCH" }).catch(() => {}); setNotifications(current => current.map(item => item.id === notification.id ? { ...item, read_at: new Date().toISOString() } : item)); setUnreadCount(current => Math.max(0, current - 1)); } setNotificationOpen(false); router.push(notification.href); }}><span className="notification-item-dot" /><span><strong>{notification.title}</strong><small>{notification.message}</small><time>{new Date(notification.created_at).toLocaleString("vi-VN", { dateStyle: "short", timeStyle: "short" })}</time></span></button>) : <div className="notification-empty"><CheckCheck size={17} />{user ? "Bạn chưa có thông báo mới." : "Đăng nhập để xem thông báo."}</div>}</div>}</div>
          {user ? <div className="account-area"><button className="account-button" onClick={() => setAccountOpen(!accountOpen)}><span className="avatar">{user.full_name.split(" ").slice(-1)[0]?.slice(0, 1)}</span><span className="account-copy"><strong>{user.full_name}</strong><small>{roleLabel(user.role)}</small></span><ChevronDown size={15} /></button>
            {accountOpen && <div className="account-menu"><div className="account-menu-user"><strong>{user.full_name}</strong><small>{user.email}</small></div><button onClick={() => { logout(); setAccountOpen(false); }}>Đăng xuất</button></div>}</div>
            : <button className="button button-primary sign-in" onClick={() => setLoginOpen(true)}><LogIn size={16} /> Đăng nhập</button>}
        </div>
      </header>
      <div className="page-content">{children}</div>
      {pathname !== "/assistant" && <Link href="/assistant" className="floating-assistant" aria-label="Mở Study AI Assistant"><span className="floating-glow" /><Bot size={22} /><span>Hỏi Study AI</span></Link>}
    </main>
    {loginOpen && <LoginDialog onClose={() => setLoginOpen(false)} />}
  </div>;
}

function roleLabel(role: string) {
  const labels: Record<string, string> = { super_admin: "Quản trị viên", admission_staff: "Tuyển sinh", student: "Sinh viên", lecturer: "Giảng viên", support_staff: "Hỗ trợ người học" };
  return labels[role] ?? "Thành viên";
}

function LoginDialog({ onClose }: { onClose: () => void }) {
  const { login } = useAuth();
  const [email, setEmail] = useState("admin@study.edu.vn");
  const [password, setPassword] = useState("StudyDemo2026!");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const submit = async (event: React.FormEvent) => {
    event.preventDefault(); setBusy(true); setError("");
    try { await login(email, password); onClose(); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Đăng nhập chưa thành công."); }
    finally { setBusy(false); }
  };
  return <div className="modal-backdrop" role="presentation" onClick={onClose}><section className="login-modal" role="dialog" aria-modal="true" aria-labelledby="login-title" onClick={event => event.stopPropagation()}>
    <button className="modal-close" onClick={onClose} aria-label="Đóng"><X size={18} /></button><div className="login-brand"><div className="brand-mark"><GraduationCap size={20} /></div><span>study<span>.</span></span></div>
    <div className="eyebrow">CHÀO MỪNG BẠN TRỞ LẠI</div><h2 id="login-title">Đăng nhập Study</h2><p className="muted-text">Đăng nhập để truy cập các nghiệp vụ theo vai trò của bạn.</p>
    <form onSubmit={submit} className="form-stack"><label>Email<input type="email" value={email} onChange={event => setEmail(event.target.value)} required autoComplete="username" /></label><label>Mật khẩu<input type="password" value={password} onChange={event => setPassword(event.target.value)} required autoComplete="current-password" /></label>
      {error && <div className="inline-error">{error}</div>}<button className="button button-primary full-width" disabled={busy}>{busy ? "Đang đăng nhập…" : "Đăng nhập"}</button></form>
    <div className="demo-credentials"><ShieldCheck size={15} /><span>Tài khoản demo: <strong>admin@study.edu.vn</strong><br />Mật khẩu: <strong>StudyDemo2026!</strong></span></div>
    <p className="fine-print">Bản demo dùng dữ liệu minh họa. Hãy thay thông tin xác thực trước khi triển khai thật.</p>
  </section></div>;
}
