import axios, { AxiosInstance } from "axios";

const baseURL = process.env.NEXT_PUBLIC_API_URL || "";

const api: AxiosInstance = axios.create({
  baseURL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor: attach token from localStorage
api.interceptors.request.use(
  (config) => {
    try {
      if (typeof window !== "undefined") {
        const token = localStorage.getItem("token");
        if (token && config.headers) {
          config.headers.Authorization = `Bearer ${token}`;
        }
      }
    } catch (e) {
      // ignore errors reading localStorage
    }
    return config;
  },
  (error) => Promise.reject(error),
);

// Response interceptor: handle 401 -> clear storage and redirect to /login
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error?.response?.status;
    if (status === 401) {
      try {
        if (typeof window !== "undefined") {
          localStorage.clear();
          window.location.href = "/login";
        }
      } catch (e) {
        // ignore
      }
    }
    return Promise.reject(error);
  },
);

export default api;
