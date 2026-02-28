import { useQuery } from "@tanstack/react-query";
import { sessionsApi } from "@/api/sessions";
import { SessionForm } from "./SessionForm";
import "./MovieSessions.css";

interface Props {
  movieId: number;
}

export function MovieSessions({ movieId }: Props) {
  const { data, isLoading } = useQuery({
    queryKey: ["sessions", "movie", movieId],
    queryFn: async () => {
      const res = await sessionsApi.getByMovie(movieId);
      return res.data;
    },
  });

  const sessions = data ?? [];

  const formatDate = (s: string) => {
    const d = new Date(s);
    return d.toLocaleString("uk-UA", {
      day: "numeric",
      month: "long",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <div className="movie-sessions">
      <h2>Сеанси</h2>
      <SessionForm movieId={movieId} />
      {isLoading ? (
        <p>Завантаження...</p>
      ) : sessions.length === 0 ? (
        <p className="empty">Немає активних сеансів</p>
      ) : (
        <ul>
          {sessions.map((s) => (
            <li key={s.id}>
              <span className="date">{formatDate(s.date)}</span>
              <span className="hall">Зал {s.hall_number}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
