export const API_BASE = (process.env.NEXT_PUBLIC_API_URL?.trim() || "http://localhost:8000/api/v1").replace(/\/+$/, "");

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) { super(message); this.status = status; }
}

export function apiErrorMessage(value: unknown, fallback = "Có lỗi xảy ra. Vui lòng thử lại."): string {
  if (typeof value === "string") return value;
  if (Array.isArray(value)) {
    const messages = value.map(item => {
      if (typeof item === "string") return item;
      if (!item || typeof item !== "object") return null;
      const entry = item as Record<string, unknown>;
      const message = typeof entry.msg === "string" ? entry.msg : typeof entry.message === "string" ? entry.message : null;
      const location = Array.isArray(entry.loc) ? entry.loc.filter(part => typeof part === "string").slice(-1)[0] as string | undefined : undefined;
      if (!message) return null;
      if (/field required|missing/i.test(message)) return `Vui lòng nhập ${location === "email" ? "email" : location === "password" ? "mật khẩu" : location ?? "đầy đủ thông tin"}.`;
      if (/valid email/i.test(message)) return "Email chưa đúng định dạng.";
      return message;
    }).filter((message): message is string => Boolean(message));
    return messages.length ? messages.join(" ") : fallback;
  }
  if (value && typeof value === "object") {
    const record = value as Record<string, unknown>;
    for (const key of ["detail", "message", "msg", "error"]) {
      if (record[key] !== undefined) {
        const message = apiErrorMessage(record[key], "");
        if (message) return message;
      }
    }
  }
  return fallback;
}

export async function authenticatedFetch(path: string, options: RequestInit = {}): Promise<Response> {
  const browser = typeof window !== "undefined";
  const token = browser ? window.sessionStorage.getItem("study_access_token") : null;
  const formData = typeof FormData !== "undefined" && options.body instanceof FormData;
  async function send(accessToken: string | null) {
    const headers = new Headers(options.headers);
    if (!formData) headers.set("Content-Type", "application/json");
    if (accessToken) headers.set("Authorization", `Bearer ${accessToken}`);
    return fetch(`${API_BASE}${path}`, { ...options, headers, cache: "no-store" });
  }
  let response: Response;
  try { response = await send(token); }
  catch { throw new ApiError(`Không thể kết nối API tại ${API_BASE}. Hãy kiểm tra Backend đang chạy, NEXT_PUBLIC_API_URL và CORS_ORIGINS.`, 0); }
  if (response.status === 401 && browser && path !== "/auth/login" && path !== "/auth/refresh") {
    const refreshToken = window.sessionStorage.getItem("study_refresh_token");
    if (refreshToken) {
      try {
        const refreshed = await fetch(`${API_BASE}/auth/refresh`, { method: "POST", headers: { Authorization: `Bearer ${refreshToken}` }, cache: "no-store" });
        if (refreshed.ok) {
          const pair = await refreshed.json();
          window.sessionStorage.setItem("study_access_token", pair.access_token);
          window.sessionStorage.setItem("study_refresh_token", pair.refresh_token);
          if (pair.user) window.sessionStorage.setItem("study_user", JSON.stringify(pair.user));
          response = await send(pair.access_token);
        } else {
          window.sessionStorage.removeItem("study_access_token"); window.sessionStorage.removeItem("study_refresh_token"); window.sessionStorage.removeItem("study_user");
        }
      } catch { /* The original API response below carries the authentication failure. */ }
    }
  }
  return response;
}

export async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await authenticatedFetch(path, options);
  if (response.status === 204) return undefined as T;
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new ApiError(apiErrorMessage(body), response.status);
  return body as T;
}

export type User = { id: string; email: string; full_name: string; role: string };
export type Major = {
  id: string; code: string; name: string; description: string; faculty_name: string;
  duration_years: number; tuition_per_year_vnd: number; admission_quota: number;
  admission_status: string; is_demo: boolean;
};
export type Ticket = {
  id: string; code: string; owner_id: string; owner_name: string; category: string;
  subject: string; description: string; priority: string; status: string; assignee_id?: string;
  satisfaction_rating: number | null; satisfaction_feedback: string | null;
  created_at: string; messages: { id: string; author_id: string; body: string; created_at: string }[];
  attachments: { id: string; filename: string; media_type: string; size_bytes: number; uploaded_at: string }[];
};
