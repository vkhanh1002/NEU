import { describe, expect, it } from "vitest";
import { apiErrorMessage } from "./api";

describe("API error messages", () => {
  it("keeps backend string details readable", () => {
    expect(apiErrorMessage({ detail: "Email hoặc mật khẩu không chính xác." })).toBe("Email hoặc mật khẩu không chính xác.");
  });

  it("translates FastAPI validation arrays instead of rendering objects", () => {
    expect(apiErrorMessage({ detail: [{ loc: ["body", "password"], msg: "Field required", type: "missing" }] })).toBe("Vui lòng nhập mật khẩu.");
  });

  it("never converts unknown error objects to [object Object]", () => {
    expect(apiErrorMessage({ detail: { code: "invalid_credentials" } })).toBe("Có lỗi xảy ra. Vui lòng thử lại.");
  });
});
