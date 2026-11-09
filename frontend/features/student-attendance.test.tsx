import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { api } from "@/lib/api";
import { StudentAttendance } from "./student-attendance";

vi.mock("@/lib/api", () => ({
  api: vi.fn(),
  authenticatedFetch: vi.fn(),
  ApiError: class ApiError extends Error {
    status: number;
    constructor(message: string, status: number) { super(message); this.status = status; }
  },
  apiErrorMessage: vi.fn(() => "Không tải được ảnh minh chứng."),
}));

afterEach(() => { cleanup(); vi.clearAllMocks(); });

describe("student attendance history connection state", () => {
  it("shows a retry instead of claiming the history is empty after a network failure", async () => {
    vi.mocked(api).mockRejectedValueOnce(new Error("Backend không phản hồi."));
    render(<StudentAttendance />);

    expect(await screen.findByRole("alert")).toHaveTextContent("Backend không phản hồi.");
    expect(screen.queryByText("Chưa có phiên điểm danh của các lớp bạn đăng ký.")).not.toBeInTheDocument();
    expect(screen.getByText("Chưa thể tải lịch sử điểm danh. Hãy thử lại khi Backend kết nối được.")).toBeInTheDocument();

    vi.mocked(api).mockResolvedValueOnce({
      items: [],
      summary: { completed_sessions: 0, present: 0, late: 0, absent: 0, participation_rate: null },
    });
    fireEvent.click(screen.getByRole("button", { name: "Thử lại" }));
    await waitFor(() => expect(screen.getByText("Chưa có phiên điểm danh của các lớp bạn đăng ký.")).toBeInTheDocument());
  });
});
