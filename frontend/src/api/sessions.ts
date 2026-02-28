import { api } from "./client";
import type { Session } from "@/types";

export const sessionsApi = {
  getAll: (movieId?: number) =>
    api.get<Session[]>("/sessions/", {
      params: movieId ? { movie: movieId } : undefined,
    }),
  getByMovie: (movieId: number) =>
    api.get<Session[]>(`/movies/${movieId}/sessions/`),
  create: (data: Partial<Session>) => api.post<Session>("/sessions/", data),
  update: (id: number, data: Partial<Session>) =>
    api.patch<Session>(`/sessions/${id}/`, data),
  delete: (id: number) => api.delete(`/sessions/${id}/`),
};
