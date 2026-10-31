import type { Metadata } from "next";
import { AuthProvider } from "@/lib/auth-context";
import { Shell } from "@/components/shell";
import "./globals.css";

export const metadata: Metadata = {
  title: "Study — University Management System",
  description: "Nền tảng quản lý đại học tập trung, tích hợp Study AI Assistant.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="vi"><body><AuthProvider><Shell>{children}</Shell></AuthProvider></body></html>;
}
