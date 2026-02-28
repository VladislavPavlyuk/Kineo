import axios from "axios";

export const api = axios.create({
  baseURL: "/api",
  headers: { "Content-Type": "application/json" },
});

export const mediaUrl = (path: string | null) =>
  path
    ? path.startsWith("http") || path.startsWith("/")
      ? path
      : `/media/${path}`
    : null;
