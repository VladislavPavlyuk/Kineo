import { api } from "./client";
import type { Review } from "@/types";

export const reviewsApi = {
  getByMovie: (movieId: number) =>
    api.get<Review[]>(`/movies/${movieId}/reviews/`),
  create: (movieId: number, data: { username: string; text: string; rating: number }) =>
    api.post<Review>(`/movies/${movieId}/reviews/`, data),
};
