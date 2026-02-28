import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { sessionsApi } from "@/api/sessions";
import "./SessionsTab.css";

export function SessionsTab() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["sessions", "all"],
    queryFn: async () => {
      const res = await sessionsApi.getAll();
      return res.data;
    },
  });

  const sessions = data ?? [];

  const formatDate = (s: string) => {
    const d = new Date(s);
    return d.toLocaleString("uk-UA", {
      weekday: "short",
      day: "numeric",
      month: "short",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  if (isLoading) return <div className="loading">Завантаження...</div>;
  if (error) return <div className="error">Помилка</div>;

  return (
    <section className="sessions-tab">
      <h1>Найближчі сеанси</h1>
      {sessions.length === 0 ? (
        <p className="empty">Немає активних сеансів</p>
      ) : (
        <div className="sessions-list">
          {sessions.map((s) => (
            <Link
              key={s.id}
              to={`/movies/${s.movie}`}
              className="session-card"
            >
              <div className="session-movie">{s.movie_title}</div>
              <div className="session-details">
                <span className="date">{formatDate(s.date)}</span>
                <span className="hall">Зал {s.hall_number}</span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </section>
  );
}
