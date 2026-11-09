"use client";

import Link from "next/link";
import { ArrowRight, Award, CalendarDays, GraduationCap, Landmark, LibraryBig, Microscope, UsersRound } from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { Dashboard } from "@/features/dashboard";
import { StudentStudyDashboard } from "@/features/student-dashboard";
import { LecturerDashboard } from "@/features/lecturer-dashboard";
import { NeuMark, NEU_CAMPUS_IMAGE_URL } from "@/components/neu-mark";

const milestones = [
  { year: "1956", title: "Trường Kinh tế Tài chính", text: "Thành lập ngày 25/01 theo Nghị định số 678-TTg." },
  { year: "1958", title: "Trường Đại học Kinh tế Tài chính", text: "Đổi tên ngày 22/05." },
  { year: "1965", title: "Trường Đại học Kinh tế Kế hoạch", text: "Bước vào giai đoạn đào tạo kinh tế kế hoạch." },
  { year: "1985", title: "Trường Đại học Kinh tế Quốc dân", text: "Mang tên NEU từ ngày 22/10." },
  { year: "2024", title: "Đại học Kinh tế Quốc dân", text: "Chuyển đổi mô hình theo Quyết định 1386/QĐ-TTg." },
];

export default function HomePage() {
  const { user, ready } = useAuth();
  if (!ready) return <div className="public-home-loading">Đang tải Cổng thông tin NEU…</div>;
  if (user) return user.role === "student" ? <StudentStudyDashboard /> : user.role === "lecturer" ? <LecturerDashboard /> : <Dashboard />;
  return <main className="public-home">
    <section className="neu-hero"><div className="neu-hero-photo" style={{ backgroundImage: `url(${NEU_CAMPUS_IMAGE_URL})` }} /><div className="neu-hero-shade" /><div className="neu-hero-content"><div className="neu-hero-brand"><NeuMark /><span>ĐẠI HỌC KINH TẾ QUỐC DÂN</span></div><span className="neu-kicker">NATIONAL ECONOMICS UNIVERSITY · HANOI</span><h1>Đại học Kinh tế<br /><em>Quốc dân</em></h1><p>Tiên phong phát triển tri thức về kinh tế, quản lý và quản trị kinh doanh; đào tạo nguồn nhân lực chất lượng cao, đóng góp cho sự phát triển bền vững.</p><div className="neu-hero-actions"><Link className="button button-primary" href="/admissions">Tìm hiểu tuyển sinh <ArrowRight size={16} /></Link><Link className="neu-hero-secondary" href="/news">Tin tức và sự kiện</Link></div></div><span className="neu-hero-caption">Ảnh khu vực sảnh do bạn cung cấp</span></section>

    <section className="neu-anniversary"><div className="anniversary-mark"><strong>70</strong><span>NĂM</span></div><div><span className="neu-section-label">1956 — 2026</span><h2>70 năm xây dựng và phát triển</h2><p>Đánh dấu bảy thập kỷ đào tạo, nghiên cứu và kết nối cộng đồng NEU qua nhiều thế hệ.</p></div><Link href="/news" className="anniversary-link">Theo dõi chuỗi sự kiện <ArrowRight size={16} /></Link></section>

    <section className="neu-intro"><div><span className="neu-section-label">VỀ NEU</span><h2>Tri thức kinh tế<br />gắn với phát triển đất nước.</h2></div><p>Đại học Kinh tế Quốc dân là cơ sở giáo dục đại học tại Hà Nội, hoạt động trong các lĩnh vực kinh tế, quản lý và quản trị kinh doanh. NEU công bố sứ mệnh tiên phong đổi mới, phát triển và phổ biến tri thức; đào tạo nhân tài và tư vấn chính sách kinh tế – xã hội.</p></section>

    <section className="neu-mission-grid" aria-label="Sứ mệnh, tầm nhìn và tinh thần">
      <article><span><GraduationCap size={22} /></span><small>SỨ MỆNH</small><h3>Phát triển tri thức</h3><p>Đào tạo nhân lực chất lượng cao, nghiên cứu và phổ biến tri thức về kinh tế, quản lý và quản trị kinh doanh.</p></article>
      <article><span><Landmark size={22} /></span><small>TẦM NHÌN ĐƯỢC CÔNG BỐ</small><h3>Đại học nghiên cứu, đa ngành</h3><p>NEU đặt mục tiêu phát triển thành đại học nghiên cứu, đa ngành, đa lĩnh vực; mục tiêu xếp hạng được nêu trên trang chính thức là định hướng phát triển.</p></article>
      <article><span><UsersRound size={22} /></span><small>THÔNG ĐIỆP 70 NĂM</small><h3>Đổi mới sáng tạo – Khát vọng vươn xa</h3><p>Thông điệp của chuỗi hoạt động năm 2026 kết nối truyền thống với đổi mới và hội nhập.</p></article>
    </section>
    <div className="neu-source-line"><a href="https://neu.edu.vn/su-menh-va-tam-nhin/" target="_blank" rel="noreferrer">Nguồn: Sứ mệnh và tầm nhìn NEU <ArrowRight size={14} /></a><a href="https://dec.neu.edu.vn/khoi-dong-chuoi-su-kien-ky-niem-70-nam-thanh-lap-va-cong-bo-bo-nhan-dien-thuong-hieu-dai-hoc-kinh-te-quoc-dan" target="_blank" rel="noreferrer">Thông điệp kỷ niệm 70 năm <ArrowRight size={14} /></a></div>

    <section className="neu-history"><div className="neu-section-heading"><div><span className="neu-section-label">HÀNH TRÌNH</span><h2>Từ năm 1956 đến hôm nay</h2></div><a href="https://login.neu.edu.vn/vi/gioi-thieu-ve-dai-hoc/lich-su-hinh-thanh-va-phat-trien-dai-hoc" target="_blank" rel="noreferrer">Xem lịch sử NEU <ArrowRight size={15} /></a></div><div className="neu-timeline">{milestones.map(item => <article key={item.year}><strong>{item.year}</strong><div><h3>{item.title}</h3><p>{item.text}</p></div></article>)}</div></section>

    <section className="neu-campus"><div className="neu-campus-heading"><span className="neu-section-label">KHÔNG GIAN NEU</span><h2>Học tập, nghiên cứu và kết nối</h2><p>Ảnh tư liệu và thông tin không gian được dẫn từ các kênh chính thức của Đại học.</p></div><div className="neu-photo-grid"><a href="https://neu.edu.vn/" target="_blank" rel="noreferrer"><img src="https://neu.edu.vn/wp-content/uploads/2026/03/z7602765192666_15e2feede34b749cf4b4df9bfbced6c5.webp" alt="Ảnh tư liệu trên website Đại học Kinh tế Quốc dân" /><span>Ảnh tư liệu NEU</span></a><a href="https://neu.edu.vn/ban-do-duong-di/" target="_blank" rel="noreferrer"><img src="https://neu.edu.vn/wp-content/uploads/2026/03/z7602765192653_e759735273493507faa32678d5178c79.webp" alt="Không gian và hoạt động tại NEU, ảnh từ website chính thức" /><span>Khuôn viên và hoạt động</span></a></div><div className="neu-campus-links"><a href="https://neu.edu.vn/ban-do-duong-di/" target="_blank" rel="noreferrer"><Landmark size={18} /> Bản đồ và đường đi</a><a href="https://neulib.neu.edu.vn/" target="_blank" rel="noreferrer"><LibraryBig size={18} /> Thư viện</a><a href="https://khoahoc.neu.edu.vn/" target="_blank" rel="noreferrer"><Microscope size={18} /> Nghiên cứu khoa học</a></div></section>

    <section className="neu-achievements"><div className="neu-section-heading"><div><span className="neu-section-label">DẤU ẤN ĐƯỢC GHI NHẬN</span><h2>Thành tựu và truyền thống</h2></div><a href="https://neu.edu.vn/he-thong-nhan-dien/" target="_blank" rel="noreferrer">Nguồn NEU <ArrowRight size={15} /></a></div><div className="neu-award-grid"><article><Award size={23} /><strong>Huân chương Hồ Chí Minh</strong><span>2001, 2011</span></article><article><Award size={23} /><strong>Anh hùng Lao động</strong><span>2000</span></article><article><Award size={23} /><strong>Huân chương Độc lập hạng Nhất</strong><span>1996</span></article><article><Award size={23} /><strong>Huân chương Lao động hạng Nhất</strong><span>1983, 2016</span></article></div><p className="neu-achievement-note">Danh hiệu theo trang Hệ thống nhận diện của NEU; đây là những ghi nhận lịch sử, không phải bảng xếp hạng hiện hành.</p></section>

    <section className="neu-feature-grid"><Link href="/admissions" className="neu-feature-card"><span><GraduationCap /></span><small>01 · TUYỂN SINH</small><h3>Chọn hành trình<br />đại học của bạn</h3><p>Tìm hiểu quy trình đăng ký, hồ sơ và cách tra cứu thông tin từng đợt.</p><b>Thông tin tuyển sinh <ArrowRight size={15} /></b></Link><Link href="/news" className="neu-feature-card"><span><CalendarDays /></span><small>02 · TIN TỨC</small><h3>Cập nhật hoạt động<br />và sự kiện NEU</h3><p>Theo dõi bản tin, sự kiện kỷ niệm 70 năm và các hoạt động học thuật.</p><b>Tin tức và sự kiện <ArrowRight size={15} /></b></Link><div className="neu-feature-card neu-feature-note"><span><UsersRound /></span><small>03 · CỘNG ĐỒNG</small><h3>Kết nối dịch vụ<br />đại học</h3><p>Sinh viên, giảng viên và cán bộ truy cập các dịch vụ theo vai trò sau khi đăng nhập.</p><Link href="/support">Trung tâm hỗ trợ <ArrowRight size={15} /></Link></div></section>
    <section className="neu-notice"><CalendarDays size={20} /><div><strong>Lễ kỷ niệm 70 năm NEU · 11/11/2026</strong><p>Trang sự kiện chính thức công bố giờ bắt đầu 08:30 và khung giờ 08:30–23:00. Địa điểm chưa được nêu trên trang sự kiện.</p></div><a href="https://neu.edu.vn/su-kien/le-ky-niem-70-nam-thanh-lap-dai-hoc-kinh-te-quoc-dan-1956-2026-va-don-nhan-huan-chuong-lao-dong-hang-nhat/" target="_blank" rel="noreferrer" aria-label="Mở sự kiện chính thức"><ArrowRight /></a></section>
    <footer className="neu-footer"><span><NeuMark /> NEU · Đại học Kinh tế Quốc dân</span><Link href="/news">Tin tức và sự kiện</Link></footer>
  </main>;
}
