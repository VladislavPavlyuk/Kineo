import { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Swal from "sweetalert2";
import { moviesApi } from "@/api/movies";
import "./MovieForm.css";

export function MovieForm() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const isEdit = !!id;

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [year, setYear] = useState(new Date().getFullYear());
  const [duration, setDuration] = useState(90);
  const [genre, setGenre] = useState("");
  const [poster, setPoster] = useState<File | null>(null);

  const { data: movie } = useQuery({
    queryKey: ["movies", id],
    queryFn: async () => {
      const res = await moviesApi.getById(Number(id));
      return res.data;
    },
    enabled: isEdit,
  });

  useEffect(() => {
    if (movie) {
      setTitle(movie.title);
      setDescription(movie.description);
      setYear(movie.year);
      setDuration(movie.duration);
      setGenre(movie.genre);
    }
  }, [movie]);

  const createMutation = useMutation({
    mutationFn: () => {
      const fd = new FormData();
      fd.append("title", title);
      fd.append("description", description);
      fd.append("year", String(year));
      fd.append("duration", String(duration));
      fd.append("genre", genre);
      if (poster) fd.append("poster", poster);
      return moviesApi.create(fd);
    },
    onSuccess: (res) => {
      queryClient.invalidateQueries({ queryKey: ["movies"] });
      navigate(`/movies/${res.data.id}`);
      Swal.fire({ icon: "success", title: "Фільм додано" });
    },
    onError: () => Swal.fire({ icon: "error", title: "Помилка" }),
  });

  const updateMutation = useMutation({
    mutationFn: () => {
      const fd = new FormData();
      fd.append("title", title);
      fd.append("description", description);
      fd.append("year", String(year));
      fd.append("duration", String(duration));
      fd.append("genre", genre);
      if (poster) fd.append("poster", poster);
      return moviesApi.update(Number(id), fd);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["movies"] });
      navigate(`/movies/${id}`);
      Swal.fire({ icon: "success", title: "Фільм оновлено" });
    },
    onError: () => Swal.fire({ icon: "error", title: "Помилка" }),
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !genre.trim()) {
      Swal.fire({ icon: "warning", title: "Заповніть обов'язкові поля" });
      return;
    }
    if (isEdit) updateMutation.mutate();
    else createMutation.mutate();
  };

  const pending = createMutation.isPending || updateMutation.isPending;

  return (
    <section className="movie-form-section">
      <h1>{isEdit ? "Редагувати фільм" : "Додати фільм"}</h1>
      <form onSubmit={handleSubmit} className="movie-form">
        <label>
          Назва *
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
        </label>
        <label>
          Опис
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={4}
          />
        </label>
        <div className="row">
          <label>
            Рік *
            <input
              type="number"
              value={year}
              onChange={(e) => setYear(Number(e.target.value))}
              min={1900}
              max={2100}
              required
            />
          </label>
          <label>
            Тривалість (хв) *
            <input
              type="number"
              value={duration}
              onChange={(e) => setDuration(Number(e.target.value))}
              min={1}
              required
            />
          </label>
        </div>
        <label>
          Жанр *
          <input
            type="text"
            value={genre}
            onChange={(e) => setGenre(e.target.value)}
            required
          />
        </label>
        <label>
          Постер
          <input
            type="file"
            accept="image/*"
            onChange={(e) => setPoster(e.target.files?.[0] ?? null)}
          />
          {isEdit && movie?.poster && !poster && (
            <span className="hint">Поточний постер збережено</span>
          )}
        </label>
        <div className="form-actions">
          <button type="submit" className="btn btn-primary" disabled={pending}>
            {pending ? "Збереження..." : isEdit ? "Зберегти" : "Додати"}
          </button>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => navigate(-1)}
          >
            Скасувати
          </button>
        </div>
      </form>
    </section>
  );
}
