import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PageTitle, StatusBadge } from "@/components/ui";

describe("shared NEU UI", () => {
  it("renders page heading and its description", () => {
    render(<PageTitle eyebrow="TỔNG QUAN" title="Dashboard" description="Tổng quan hoạt động." />);
    expect(screen.getByRole("heading", { name: "Dashboard" })).toBeInTheDocument();
    expect(screen.getByText("Tổng quan hoạt động.")).toBeInTheDocument();
  });

  it("renders workflow status", () => {
    render(<StatusBadge>Đang xử lý</StatusBadge>);
    expect(screen.getByText("Đang xử lý")).toBeInTheDocument();
  });
});
