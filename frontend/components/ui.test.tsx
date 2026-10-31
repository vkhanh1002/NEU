import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DemoTag, PageTitle, StatusBadge } from "@/components/ui";

describe("shared Study UI", () => {
  it("renders page heading and its description", () => {
    render(<PageTitle eyebrow="TỔNG QUAN" title="Dashboard" description="Tổng quan hoạt động." />);
    expect(screen.getByRole("heading", { name: "Dashboard" })).toBeInTheDocument();
    expect(screen.getByText("Tổng quan hoạt động.")).toBeInTheDocument();
  });

  it("labels demo data and renders workflow status", () => {
    render(<><DemoTag /><StatusBadge>Đang xử lý</StatusBadge></>);
    expect(screen.getByText("Dữ liệu minh họa")).toBeInTheDocument();
    expect(screen.getByText("Đang xử lý")).toBeInTheDocument();
  });
});
