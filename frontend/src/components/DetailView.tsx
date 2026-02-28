import { useQuery } from "@tanstack/react-query";
import { useParams, Link, useNavigate } from "react-router-dom";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import Swal from "sweetalert2";
import { moviesApi } from "@/api/movies";
import { mediaUrl } from "@/api/client";
import { MovieReviews } from "./MovieReviews";
import { MovieSessions } from "./MovieSessions";
import "./DetailView.css";

export function DetailView() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const { data: movie, isLoading, error } = useQuery({
    queryKey: ["movies", id],
    queryFn: async () => {
      const res = await moviesApi.getById(Number(id));
      return res.data;
    },
    enabled: !!id,
  });

  const deleteMutation = useMutation({
    mutationFn: () => moviesApi.delete(Number(id)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["movies"] });
      navigate("/");
      Swal.fire({ icon: "success", title: "Фільм видалено" });
    },
    onError: () => {
      Swal.fire({ icon: "error", title: "Помилка видалення" });
    },
  });

  const handleDelete = () => {
    Swal.fire({
      title: "Видалити фільм?",
      showCancelButton: true,
      confirmButtonText: "Так",
      cancelButtonText: "Ні",
    }).then((r) => {
      if (r.isConfirmed) deleteMutation.mutate();
    });
  };

  if (isLoading || !id) return <div className="loading">Завантаження...</div>;
  if (error || !movie) return <div className="error">Фільм не знайдено</div>;

  return (
    <section className="detail-view">
      <div className="detail-header">
        <div className="poster-large">
          {movie.poster ? (
            <img src={mediaUrl(movie.poster)!} alt={movie.title} />
          ) : (
            <div className="poster-placeholder">Немає постеру</div>
          )}
        </div>
        <div className="detail-info">
          <h1>{movie.title}</h1>
          <p className="meta">{movie.year} · {movie.genre} · {movie.duration} хв</p>
          <p className="description">{movie.description || "Немає опису"}</p>
          <div className="actions">
            <Link to={`/movies/${id}/edit`} className="btn btn-primary">
              Редагувати
            </Link>
            <button type="button" className="btn btn-danger" onClick={handleDelete}>
              Видалити
            </button>
          </div>
        </div>
      </div>

      <MovieSessions movieId={movie.id} />
      <MovieReviews movieId={movie.id} />
    </section>
  );
}
