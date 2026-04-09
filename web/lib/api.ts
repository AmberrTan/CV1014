import type { Gym, SearchPayload } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return (await response.json()) as T;
}

export function getGyms(): Promise<Gym[]> {
  return request<Gym[]>("/api/gyms");
}

export function searchGyms(payload: SearchPayload): Promise<Gym[]> {
  return request<Gym[]>("/api/search", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function compareGyms(gymIds: number[]): Promise<Gym[]> {
  return request<Gym[]>("/api/compare", {
    method: "POST",
    body: JSON.stringify({ gym_ids: gymIds }),
  });
}

export function createGym(payload: Omit<Gym, "gym_id" | "display_hours">): Promise<Gym> {
  return request<Gym>("/api/gyms", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateGym(
  gymId: number,
  payload: Omit<Gym, "gym_id" | "display_hours">,
): Promise<Gym> {
  return request<Gym>(`/api/gyms/${gymId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}
