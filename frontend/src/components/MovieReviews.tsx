import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Swal from "sweetalert2";
import { reviewsApi } from "@/api/reviews";
import "./MovieReviews.css";

interface Props {
  movieId: number;
}

export function MovieReviews({ movieId }: Props) {
  const [username, setUsername] = useState("");
  const [text, setText] = useState("");
  const [rating, setRating] = useState(5);
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ["reviews", movieId],
    queryFn: async () => {
      const res = await reviewsApi.getByMovie(movieId);
      return res.data;
    },
  });

  const createMutation = useMutation({
    mutationFn: () =>
      reviewsApi.create(movieId, { username, text, rating }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["reviews", movieId] });
      setUsername("");
      setText("");
      setRating(5);
      Swal.fire({ icon: "success", title: "Відгук додано" });
    },
    onError: () => {
      Swal.fire({ icon: "error", title: "Помилка" });
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!username.trim() || !text.trim()) {
      Swal.fire({ icon: "warning", title: "Заповніть ім'я та текст" });
      return;
    }
    createMutation.mutate();
  };

  const reviews = data ?? [];

  const formatDate = (s: string) =>
    new Date(s).toLocaleDateString("uk-UA", {
      day: "numeric",
      month: "long",
      year: "numeric",
    });

  return (
    <div className="movie-reviews">
      <h2>Відгуки</h2>

      <form onSubmit={handleSubmit} className="review-form">
        <input
          type="text"
          placeholder="Ваше ім'я"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <textarea
          placeholder="Текст відгуку"
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows={3}
        />
        <div className="rating-row">
          <label>Оцінка:</label>
          <select value={rating} onChange={(e) => setRating(Number(e.target.value))}>
            {[1, 2, 3, 4, 5].map((n) => (
              <option key={n} value={n}>
                {n} ★
              </option>
            ))}
          </select>
        </div>
        <button type="submit" className="btn btn-primary" disabled={createMutation.isPending}>
          Додати відгук
        </button>
      </form>

      <div className="reviews-list">
        {isLoading ? (
          <p>Завантаження...</p>
        ) : reviews.length === 0 ? (
          <p className="empty">Ще немає відгуків</p>
        ) : (
          reviews.map((r) => (
            <div key={r.id} className="review-card">
              <div className="review-header">
                <strong>{r.username}</strong>
                <span className="stars">{"★".repeat(r.rating)}</span>
                <span className="date">{formatDate(r.created_at)}</span>
              </div>
              <p>{r.text}</p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
