"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { Bot, Bell, BookOpen, CheckCheck, ChevronDown, ChevronLeft, ChevronRight, CircleHelp, GraduationCap, LayoutDashboard, LogIn, Menu, Search, UsersRound, BriefcaseBusiness, UserRound, X, ClipboardList, CalendarDays, Award, Wallet, FileCheck2, Send, Sparkles, ShieldCheck } from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { api } from "@/lib/api";
import { DEMO_ACCOUNTS, DemoRole } from "@/lib/demo-accounts";
import { GuestChat } from "@/features/guest-chat";

type NavigationLink = { label: string; href: string; icon: typeof LayoutDashboard; roles?: string[] };
const publicNavigation: { title: string; links: NavigationLink[] }[] = [
  { title: "NEU", links: [
    { label: "Giới thiệu", href: "/", icon: GraduationCap },
    { label: "Tuyển sinh", href: "/admissions", icon: ClipboardList },
    { label: "Tin tức và sự kiện", href: "/news", icon: CalendarDays },
  ] },
];
const applicantNavigation: { title: string; links: NavigationLink[] }[] = [
  ...publicNavigation,
  { title: "TÀI KHOẢN", links: [{ label: "Hồ sơ của tôi", href: "/admissions", icon: FileCheck2 }] },
];
const studentNavigation: { title: string; links: NavigationLink[] }[] = [
  { title: "HỌC TẬP", links: [
    { label: "Tiến độ học tập", href: "/", icon: LayoutDashboard },
    { label: "Thông tin cá nhân", href: "/profiles", icon: UsersRound },
    { label: "Thời khóa biểu", href: "/student/schedule", icon: CalendarDays },
    { label: "Lịch thi", href: "/student/exams", icon: CalendarDays },
    { label: "Kết quả học tập", href: "/student/results", icon: Award },
    { label: "Kết quả rèn luyện", href: "/student/conduct", icon: FileCheck2 },
    { label: "Tài chính sinh viên", href: "/student/finance", icon: Wallet },
    { label: "Bài tập và hạn nộp", href: "/student/assignments", icon: ClipboardList },
  ] },
  { title: "DỊCH VỤ", links: [
    { label: "Thông báo", href: "/notifications", icon: Bell },
    { label: "Yêu cầu hỗ trợ", href: "/support", icon: CircleHelp },
  ] },
];
const lecturerNavigation: { title: string; links: NavigationLink[] }[] = [
  { title: "GIẢNG DẠY", links: [
    { label: "Dashboard", href: "/", icon: LayoutDashboard },
    { label: "Thời khóa biểu giảng dạy", href: "/lecturer/schedule", icon: CalendarDays },
  ] },
];
const navigation: { title: string; links: NavigationLink[] }[] = [
  { title: "TỔNG QUAN", links: [{ label: "Dashboard", href: "/", icon: LayoutDashboard, roles: ["super_admin", "admission_staff", "lecturer", "support_staff", "hr_staff", "academic_staff"] }] },
  { title: "TUYỂN SINH", links: [{ label: "Hồ sơ thí sinh", href: "/admissions", icon: GraduationCap, roles: ["super_admin", "admission_staff"] }] },
  { title: "HỒ SƠ", links: [
    { label: "Hồ sơ sinh viên", href: "/profiles", icon: UsersRound, roles: ["super_admin", "support_staff", "academic_staff"] },
    { label: "Hồ sơ giảng viên", href: "/personnel/lecturers", icon: GraduationCap, roles: ["super_admin", "hr_staff"] },
    { label: "Hồ sơ nhân viên", href: "/personnel/employees", icon: BriefcaseBusiness, roles: ["super_admin", "hr_staff"] },
  ] },
  { title: "DỊCH VỤ NGƯỜI HỌC", links: [
    { label: "Yêu cầu hỗ trợ", href: "/support", icon: CircleHelp, roles: ["super_admin", "student", "support_staff"] },
    { label: "Kho tri thức", href: "/admin", icon: BookOpen, roles: ["super_admin"] },
  ] },
  { title: "NHÂN SỰ", links: [{ label: "Tổng quan nhân sự", href: "/personnel", icon: UserRound, roles: ["super_admin", "hr_staff"] }] },
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
  const [guestChatOpen, setGuestChatOpen] = useState(false);
  const [notifications, setNotifications] = useState<{ id: string; title: string; message: string; href: string; read_at: string | null; created_at: string }[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  useEffect(() => {
    const open = () => setGuestChatOpen(true);
    window.addEventListener("neu:open-assistant", open);
    return () => window.removeEventListener("neu:open-assistant", open);
  }, []);
  const roleHome: Record<string, string> = { student: "/", applicant: "/admissions", lecturer: "/", admission_staff: "/admissions", hr_staff: "/personnel", support_staff: "/support", academic_staff: "/profiles", super_admin: "/" };
  const visibleNavigation = !user ? publicNavigation : user.role === "student" ? studentNavigation : user.role === "applicant" ? applicantNavigation : user.role === "lecturer" ? lecturerNavigation : navigation.map(group => ({ ...group, links: group.links.filter(link => !link.roles || link.roles.includes(user.role)).map(link => link.href === "/support" && user.role === "support_staff" ? { ...link, label: "Danh sách yêu cầu" } : link) })).filter(group => group.links.length > 0);
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
  const title = [...publicNavigation, ...studentNavigation, ...navigation].flatMap(group => group.links).find(link => link.href === pathname)?.label ?? "NEU";
  const search = (event: React.FormEvent) => {
    event.preventDefault();
    if (!query.trim()) return;
    router.push(`/admissions?search=${encodeURIComponent(query.trim())}`);
  };
  useEffect(() => {
    if (!user || pathname !== "/") return;
    const destination = roleHome[user.role] ?? "/";
    if (destination !== "/") router.replace(destination);
  }, [user?.role, pathname]);
  const pathRoles: Record<string, string[]> = {
    "/profiles": ["super_admin", "student", "support_staff", "academic_staff"],
    "/personnel": ["super_admin", "hr_staff"], "/personnel/lecturers": ["super_admin", "hr_staff"],
    "/personnel/employees": ["super_admin", "hr_staff"], "/admin": ["super_admin"],
    "/lecturer/schedule": ["lecturer"],
    "/support": ["super_admin", "student", "support_staff"],
    "/assistant": ["super_admin", "student", "applicant", "lecturer", "support_staff", "admission_staff", "hr_staff", "academic_staff"],
  };
  const restrictedRoles = pathRoles[pathname] ?? (pathname.startsWith("/student/") || pathname === "/notifications" ? ["student"] : undefined);
  useEffect(() => {
    if (user && restrictedRoles && !restrictedRoles.includes(user.role)) router.replace(roleHome[user.role] ?? "/");
    if (!user && restrictedRoles) router.replace("/");
  }, [user?.role, pathname]);

  return <div className={`app-shell ${collapsed ? "sidebar-collapsed" : ""}`}>
    {mobileOpen && <button className="mobile-scrim" onClick={() => setMobileOpen(false)} aria-label="Đóng menu" />}
    <aside className={`sidebar ${mobileOpen ? "mobile-open" : ""}`}>
      <div className="sidebar-brand-row"><Link href="/" className="brand" onClick={() => setMobileOpen(false)}>
        <div className="brand-mark"><GraduationCap size={21} strokeWidth={2.3} /></div>
        <div className="brand-name"><strong>NEU</strong><small>ĐẠI HỌC KINH TẾ QUỐC DÂN</small></div>
      </Link><button className="mobile-close" onClick={() => setMobileOpen(false)} aria-label="Đóng"><X size={18} /></button></div>
      <div className="workspace-picker"><div className="campus-avatar">N</div><div className="workspace-name"><strong>Đại học Kinh tế Quốc dân</strong><small>Cổng thông tin NEU</small></div><ChevronDown size={15} /></div>
      <nav className="side-nav">
        {visibleNavigation.map(group => <div className="nav-group" key={group.title}>
          <div className="nav-group-title">{group.title}</div>
          {group.links.map(item => <Link href={item.href} key={item.href} onClick={() => setMobileOpen(false)} title={collapsed ? item.label : undefined}
            className={`nav-link ${pathname === item.href ? "active" : ""}`}><item.icon size={18} strokeWidth={1.8} /><span>{item.label}</span>{item.href === "/assistant" && <span className="nav-new">AI</span>}</Link>)}
        </div>)}
      </nav>
      <div className="sidebar-bottom">
        <button className="collapse-button" onClick={() => setCollapsed(!collapsed)}><ChevronLeft className="collapse-icon" size={17} /><span>Thu gọn menu</span></button>
        <div className="sidebar-foot"><span className="online-dot" />Hệ thống hoạt động <span className="version">v1.0.0</span></div>
      </div>
    </aside>
    <main className="main-column">
      <header className="topbar">
        <div className="topbar-left"><button className="mobile-menu" onClick={() => setMobileOpen(true)} aria-label="Mở menu"><Menu size={21} /></button><div className="breadcrumbs"><span>NEU</span><span>/</span><strong>{title}</strong></div></div>
        <div className="topbar-actions">
          {user && <form className="global-search" onSubmit={search}><Search size={16} /><input value={query} onChange={event => setQuery(event.target.value)} placeholder="Tìm nhanh ngành, hồ sơ…" aria-label="Tìm kiếm" /><kbd>⌘ K</kbd></form>}
          {user && <div className="notification-wrap"><button className="icon-button notification-button" title="Thông báo" onClick={() => { setNotificationOpen(!notificationOpen); setAccountOpen(false); }}><Bell size={18} />{unreadCount > 0 && <i />}</button>{notificationOpen && <div className="notification-menu"><div className="notification-heading"><strong>Thông báo</strong><span>{unreadCount ? `${unreadCount} chưa đọc` : "Đã cập nhật"}</span></div>{notifications.length ? notifications.slice(0, 8).map(notification => <button className={`notification-item ${notification.read_at ? "" : "unread"}`} key={notification.id} onClick={async () => { if (!notification.read_at) { await api(`/notifications/${notification.id}/read`, { method: "PATCH" }).catch(() => {}); setNotifications(current => current.map(item => item.id === notification.id ? { ...item, read_at: new Date().toISOString() } : item)); setUnreadCount(current => Math.max(0, current - 1)); } setNotificationOpen(false); router.push(notification.href); }}><span className="notification-item-dot" /><span><strong>{notification.title}</strong><small>{notification.message}</small><time>{new Date(notification.created_at).toLocaleString("vi-VN", { dateStyle: "short", timeStyle: "short" })}</time></span></button>) : <div className="notification-empty"><CheckCheck size={17} />Bạn chưa có thông báo mới.</div>}</div>}</div>}
          {user ? <div className="account-area"><button className="account-button" onClick={() => setAccountOpen(!accountOpen)}><span className="avatar">{user.full_name.split(" ").slice(-1)[0]?.slice(0, 1)}</span><span className="account-copy"><strong>{user.full_name}</strong><small>{roleLabel(user.role)}</small></span><ChevronDown size={15} /></button>
            {accountOpen && <div className="account-menu"><div className="account-menu-user"><strong>{user.full_name}</strong><small>{user.email}</small></div><button onClick={() => { logout(); setAccountOpen(false); }}>Đăng xuất</button></div>}</div>
            : <button className="button button-primary sign-in" onClick={() => setLoginOpen(true)}><LogIn size={16} /> Đăng nhập</button>}
        </div>
      </header>
      <div className="page-content">{(restrictedRoles && (!user || !restrictedRoles.includes(user.role))) ? <div className="public-home-loading">Đang chuyển đến khu vực phù hợp với tài khoản…</div> : children}</div>
      {pathname !== "/assistant" && (user ? <Link href="/assistant" className="floating-assistant" aria-label="Mở trợ lý NEU"><span className="floating-glow" /><Bot size={22} /><span>Hỏi trợ lý</span></Link> : <>
        <GuestChat open={guestChatOpen} onClose={() => setGuestChatOpen(false)} />
        <button className="floating-assistant" aria-label="Mở trợ lý tư vấn" onClick={() => setGuestChatOpen(current => !current)}><span className="floating-glow" /><Bot size={22} /><span>Hỏi tư vấn</span></button>
      </>)}
    </main>
    {loginOpen && <LoginDialog onClose={() => setLoginOpen(false)} />}
  </div>;
}

function roleLabel(role: string) {
  const labels: Record<string, string> = { super_admin: "Quản trị viên", admission_staff: "Cán bộ tuyển sinh", applicant: "Thí sinh", student: "Sinh viên", lecturer: "Giảng viên", support_staff: "Hỗ trợ người học", hr_staff: "Cán bộ nhân sự", academic_staff: "Cán bộ đào tạo" };
  return labels[role] ?? "Thành viên";
}

function LoginDialog({ onClose }: { onClose: () => void }) {
  const { login } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [selectedDemoRole, setSelectedDemoRole] = useState<DemoRole | null>(null);
  const submit = async (event: React.FormEvent) => {
    event.preventDefault(); setBusy(true); setError("");
    try { const signedIn = await login(email, password); onClose(); router.replace(({ student: "/", applicant: "/admissions", lecturer: "/", admission_staff: "/admissions", hr_staff: "/personnel", support_staff: "/support", academic_staff: "/profiles", super_admin: "/" } as Record<string, string>)[signedIn.role] ?? "/"); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Đăng nhập chưa thành công."); }
    finally { setBusy(false); }
  };
  const selectDemo = (role: DemoRole) => {
    const account = DEMO_ACCOUNTS.find(item => item.role === role);
    if (!account) return;
    setEmail(account.email); setPassword(account.password); setSelectedDemoRole(role); setError("");
  };
  const demoIcon = (role: DemoRole) => role === "student" ? <BookOpen size={14} />
    : role === "applicant" || role === "lecturer" ? <GraduationCap size={14} />
      : role === "hr_staff" ? <BriefcaseBusiness size={14} />
        : role === "super_admin" ? <ShieldCheck size={14} />
          : role === "support_staff" ? <CircleHelp size={14} /> : <ClipboardList size={14} />;
  return <div className="modal-backdrop" role="presentation" onClick={onClose}><section className="login-modal" role="dialog" aria-modal="true" aria-labelledby="login-title" onClick={event => event.stopPropagation()}>
    <button className="modal-close" onClick={onClose} aria-label="Đóng"><X size={18} /></button><div className="login-brand"><div className="brand-mark"><GraduationCap size={20} /></div><span>NEU</span></div>
    <div className="eyebrow">CHÀO MỪNG BẠN TRỞ LẠI</div><h2 id="login-title">Đăng nhập NEU</h2><p className="muted-text">Đăng nhập để truy cập các nghiệp vụ theo vai trò của bạn.</p>
    <form onSubmit={submit} className="form-stack"><label>Email<input type="email" value={email} onChange={event => { setEmail(event.target.value); setSelectedDemoRole(null); }} required autoComplete="username" /></label><label>Mật khẩu<input type="password" value={password} onChange={event => { setPassword(event.target.value); setSelectedDemoRole(null); }} required autoComplete="current-password" /></label>
      {error && <div className="inline-error" role="alert">{error}</div>}<button className="button button-primary full-width" disabled={busy}>{busy ? "Đang đăng nhập…" : "Đăng nhập"}</button></form>
    <details className="demo-account-picker"><summary>Đăng nhập nhanh bằng tài khoản mẫu</summary><div className="demo-account-grid">{DEMO_ACCOUNTS.map(account => <button type="button" key={account.role} className={`demo-account-option ${selectedDemoRole === account.role ? "selected" : ""}`} aria-pressed={selectedDemoRole === account.role} onClick={() => selectDemo(account.role)}>{demoIcon(account.role)}<span>{account.displayName}</span></button>)}</div>
      {selectedDemoRole && <p className="demo-account-selected" role="status">Đã điền tài khoản {DEMO_ACCOUNTS.find(item => item.role === selectedDemoRole)?.displayName}. Nhấn “Đăng nhập” để tiếp tục.</p>}
      <p className="demo-account-hint">Tài khoản mẫu chỉ dùng cho môi trường phát triển.</p></details>
  </section></div>;
}
