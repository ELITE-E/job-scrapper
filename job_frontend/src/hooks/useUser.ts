"use client";

import { useQuery } from "@tanstack/react-query";
import { useAuth } from "./useAuth";
import { getUserProfile } from "@/services/userApi";

export function useUser() {
  const { isAuthenticated } = useAuth();

  return useQuery({
    queryKey: ["user", "profile"],
    queryFn: getUserProfile,
    enabled: isAuthenticated,
    staleTime: Infinity,
  });
}
