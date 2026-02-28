import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { moviesApi } from "@/api/movies";
import { mediaUrl } from "@/api/client";
import "./ListView.css";

export function ListView() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["movies"],
    queryFn: async () => {
      const res = await moviesApi.getAll();
      return res.data;
    },
  });

  if (isLoading) return <div className="loading">Завантаження...</div>;
  if (error) return <div className="error">Помилка завантаження</div>;

  const movies = data ?? [];

  return (
    <section className="list-view">
      <h1>Фільми</h1>
      <div className="movie-grid">
        {movies.map((m) => (
          <Link key={m.id} to={`/movies/${m.id}`} className="movie-card">
            <div className="poster-wrap">
              {m.poster ? (
                <img src={mediaUrl(m.poster)!} alt={m.title} />
              ) : (
                <div className="poster-placeholder">Немає постеру</div>
              )}
            </div>
            <div className="card-info">
              <h3>{m.title}</h3>
              <span className="meta">{m.year} · {m.genre} · {m.duration} хв</span>
            </div>
          </Link>
        ))}
      </div>
    </section>
  );
}
