import api from "./api";
import type { UserResponse } from "@/types/auth";

export async function getUserProfile(): Promise<UserResponse> {
  const { data } = await api.get<UserResponse>("/api/v1/users/me");
  return data;
}
