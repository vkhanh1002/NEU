"use client";

import Link from "next/link";
import { ArrowRight, CalendarDays, GraduationCap, Landmark, UsersRound } from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { Dashboard } from "@/features/dashboard";
import { StudentStudyDashboard } from "@/features/student-dashboard";

export default function HomePage() {
  const { user, ready } = useAuth();
  if (!ready) return <div className="public-home-loading">Đang tải Cổng thông tin NEU…</div>;
  if (user) return user.role === "student" ? <StudentStudyDashboard /> : <Dashboard />;
  return <main className="public-home">
    <section className="neu-hero"><div className="neu-hero-photo" /><div className="neu-hero-shade" /><div className="neu-hero-content"><span className="neu-kicker">NATIONAL ECONOMICS UNIVERSITY · HANOI</span><h1>Đại học Kinh tế<br /><em>Quốc dân</em></h1><p>Không gian thông tin dành cho người học, thí sinh và cộng đồng học thuật.</p><div className="neu-hero-actions"><Link className="button button-primary" href="/admissions">Tìm hiểu tuyển sinh <ArrowRight size={16} /></Link><Link className="neu-hero-secondary" href="/news">Tin tức và sự kiện</Link></div></div></section>
    <section className="neu-intro"><div><span className="neu-section-label">VỀ NEU</span><h2>Nơi tri thức kinh tế<br />gặp gỡ tương lai.</h2></div><p>Đại học Kinh tế Quốc dân là môi trường đào tạo, nghiên cứu và kết nối cộng đồng học thuật. Cổng thông tin hỗ trợ tra cứu dịch vụ, hướng dẫn tuyển sinh và nội dung dành cho người học.</p></section>
    <section className="neu-feature-grid"><Link href="/admissions" className="neu-feature-card"><span><GraduationCap /></span><small>01 · TUYỂN SINH</small><h3>Chọn hành trình<br />đại học của bạn</h3><p>Tìm hiểu quy trình đăng ký, hồ sơ và cách tra cứu thông tin từng đợt.</p><b>Thông tin tuyển sinh <ArrowRight size={15} /></b></Link><Link href="/news" className="neu-feature-card"><span><CalendarDays /></span><small>02 · TIN TỨC</small><h3>Cập nhật hoạt động<br />và hướng dẫn</h3><p>Đọc bài viết về học tập, kỹ năng và các chủ đề dành cho người học.</p><b>Tin tức và sự kiện <ArrowRight size={15} /></b></Link><div className="neu-feature-card neu-feature-note"><span><UsersRound /></span><small>03 · CỘNG ĐỒNG</small><h3>Kết nối dịch vụ<br />đại học</h3><p>Sinh viên, giảng viên và cán bộ truy cập dịch vụ theo vai trò sau khi đăng nhập.</p><Landmark size={17} /></div></section>
    <section className="neu-notice"><CalendarDays size={20} /><div><strong>Tra cứu thông tin tuyển sinh</strong><p>Điều kiện và thời hạn có thể phụ thuộc từng đợt. Hãy xem hướng dẫn hiện hành hoặc liên hệ đơn vị phụ trách trước khi nộp hồ sơ.</p></div><Link href="/admissions" aria-label="Mở thông tin tuyển sinh"><ArrowRight /></Link></section>
    <footer className="neu-footer"><span>NEU · Đại học Kinh tế Quốc dân</span><Link href="/news">Tin tức và sự kiện</Link></footer>
  </main>;
}
