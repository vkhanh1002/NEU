export type DemoRole = "applicant" | "student" | "lecturer" | "admission_staff" | "hr_staff" | "support_staff" | "super_admin";

export const DEMO_ACCOUNTS: {
  role: DemoRole;
  displayName: string;
  email: string;
  password: string;
  description: string;
}[] = [
  { role: "applicant", displayName: "Thí sinh", email: "candidate01@example.test", password: "NEUApplicant2026!", description: "Xem và theo dõi hồ sơ tuyển sinh." },
  { role: "student", displayName: "Sinh viên", email: "student@neu.local", password: "NEUStudent2026!", description: "Xem tiến độ, lịch học và dịch vụ sinh viên." },
  { role: "lecturer", displayName: "Giảng viên", email: "lecturer@neu.local", password: "NEUStaff2026!", description: "Mở bảng điều khiển giảng dạy." },
  { role: "admission_staff", displayName: "Cán bộ tuyển sinh", email: "admissions@neu.local", password: "NEUStaff2026!", description: "Quản lý hồ sơ tuyển sinh." },
  { role: "hr_staff", displayName: "Cán bộ nhân sự", email: "hr@neu.local", password: "NEUStaff2026!", description: "Quản lý hồ sơ nhân sự." },
  { role: "support_staff", displayName: "Công tác sinh viên", email: "support@neu.local", password: "NEUStaff2026!", description: "Tiếp nhận và xử lý hỗ trợ người học." },
  { role: "super_admin", displayName: "Quản trị viên", email: "admin@neu.local", password: "NEUStaff2026!", description: "Truy cập khu vực quản trị." },
];
