import { ChatResponse, CollectionsResponse, LoginResponse } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = await response.json();
      detail = body.detail ?? detail;
    } catch {
      // ignore non-JSON error bodies
    }
    throw new ApiError(response.status, detail);
  }

  return response.json() as Promise<T>;
}

export function login(username: string, password: string): Promise<LoginResponse> {
  return request<LoginResponse>("/login", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });
}

export function sendChatMessage(question: string, token: string): Promise<ChatResponse> {
  return request<ChatResponse>("/chat", {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: JSON.stringify({ question }),
  });
}

export function getCollections(role: string, token: string): Promise<CollectionsResponse> {
  return request<CollectionsResponse>(`/collections/${role}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
}

export function checkHealth(): Promise<{ status: string; database_connected: boolean }> {
  return request("/health");
}
