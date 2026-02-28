import { api } from "./client";
import type { Movie } from "@/types";

export const moviesApi = {
  getAll: () => api.get<Movie[]>("/movies/"),
  getById: (id: number) => api.get<Movie>(`/movies/${id}/`),
  create: (data: FormData) =>
    api.post<Movie>("/movies/", data, {
      headers: { "Content-Type": "multipart/form-data" },
    }),
  update: (id: number, data: FormData) =>
    api.patch<Movie>(`/movies/${id}/`, data, {
      headers: { "Content-Type": "multipart/form-data" },
    }),
  delete: (id: number) => api.delete(`/movies/${id}/`),
};
