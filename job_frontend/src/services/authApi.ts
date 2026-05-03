import api from "./api";
import type { UserResponse } from "@/types/auth";

export async function login(
  email: string,
  password: string,
): Promise<{ access_token: string; token_type: string }> {
  const body = new URLSearchParams({ username: email, password });
  const { data } = await api.post("/api/v1/auth/login", body.toString(), {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
  return data;
}

export async function register(
  email: string,
  password: string,
  full_name?: string,
): Promise<UserResponse> {
  const payload: Record<string, unknown> = { email, password };
  if (full_name) payload.full_name = full_name;
  const { data } = await api.post<UserResponse>(
    "/api/v1/auth/register",
    payload,
  );
  return data;
}
