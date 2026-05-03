"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { login as loginAPI } from "@/services/authApi";

export function useAuth() {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Initialize token from localStorage on mount
  useEffect(() => {
    const storedToken = localStorage.getItem("token");
    setToken(storedToken);
    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string): Promise<void> => {
    try {
      setIsLoading(true);
      const response = await loginAPI(email, password);
      const newToken = response.access_token;
      localStorage.setItem("token", newToken);
      setToken(newToken);
      router.push("/jobs");
    } finally {
      setIsLoading(false);
    }
  };

  const logout = (): void => {
    localStorage.removeItem("token");
    setToken(null);
    router.push("/");
  };

  return {
    token,
    isAuthenticated: !!token,
    isLoading,
    login,
    logout,
  };
}
