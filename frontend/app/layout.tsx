import type { Metadata } from "next";
import { AuthProvider } from "@/lib/auth-context";
import { Shell } from "@/components/shell";
import "./globals.css";

export const metadata: Metadata = {
  title: "NEU | Hệ thống quản lý đại học",
  description: "Cổng thông tin và dịch vụ của Đại học Kinh tế Quốc dân.",
  icons: { icon: "/neu-mark.svg" },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="vi"><body><AuthProvider><Shell>{children}</Shell></AuthProvider></body></html>;
}
