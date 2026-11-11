const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

export type User = {
  id: string;
  email: string;
  email_verified: boolean;
  display_name: string;
  locale: string;
};

export type Organization = {
  id: string;
  name: string;
};

export type Course = {
  id: string;
  organization_id: string;
  name: string;
  description: string | null;
  archived_at: string | null;
  created_at: string;
  updated_at: string;
};

type ApiErrorResponse = {
  error?: {
    code?: string;
    message?: string;
  };
};

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
    readonly code: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

function csrfToken(): string | undefined {
  if (typeof document === "undefined") return undefined;
  const cookieName = window.location.protocol === "https:" ? "__Host-study_csrf" : "study_csrf";
  const prefix = `${cookieName}=`;
  const cookie = document.cookie.split("; ").find((entry) => entry.startsWith(prefix));
  return cookie ? decodeURIComponent(cookie.slice(prefix.length)) : undefined;
}

export async function apiRequest<T>(
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const headers = new Headers(init.headers);
  if (init.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  const method = (init.method ?? "GET").toUpperCase();
  if (!["GET", "HEAD", "OPTIONS"].includes(method)) {
    const csrf = csrfToken();
    if (csrf) headers.set("X-CSRF-Token", csrf);
  }

  let response: Response;
  try {
    response = await fetch(`${apiBaseUrl}${path}`, {
      ...init,
      method,
      headers,
      credentials: "include",
    });
  } catch {
    throw new ApiError("The service could not be reached. Check your connection and retry.", 0, "network_error");
  }

  if (response.status === 204) return undefined as T;
  const result = (await response.json().catch(() => ({}))) as ApiErrorResponse & T;
  if (!response.ok) {
    throw new ApiError(
      result.error?.message ?? "The request could not be completed.",
      response.status,
      result.error?.code ?? "request_failed",
    );
  }
  return result as T;
}
