
import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL;

if (!API_URL) {
  console.warn("NEXT_PUBLIC_API_URL is not configured.");
}

const api = axios.create({
  baseURL: API_URL?.replace(/\/+$/, ""),
  headers: {
    Accept: "application/json",
  },
});

// Automatically attach the JWT to authenticated requests.
api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("access_token");

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }

  return config;
});

export default api;
