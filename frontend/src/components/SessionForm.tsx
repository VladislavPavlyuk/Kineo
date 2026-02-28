import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import Swal from "sweetalert2";
import { sessionsApi } from "@/api/sessions";
import "./SessionForm.css";

interface Props {
  movieId: number;
  onSuccess?: () => void;
}

export function SessionForm({ movieId, onSuccess }: Props) {
  const [date, setDate] = useState("");
  const [hallNumber, setHallNumber] = useState(1);
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: () =>
      sessionsApi.create({
        movie: movieId,
        date: new Date(date).toISOString(),
        hall_number: hallNumber,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["sessions"] });
      queryClient.invalidateQueries({ queryKey: ["sessions", "movie", movieId] });
      setDate("");
      setHallNumber(1);
      Swal.fire({ icon: "success", title: "Сеанс додано" });
      onSuccess?.();
    },
    onError: () => Swal.fire({ icon: "error", title: "Помилка" }),
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!date) {
      Swal.fire({ icon: "warning", title: "Оберіть дату" });
      return;
    }
    mutation.mutate();
  };

  const minDate = new Date().toISOString().slice(0, 16);

  return (
    <form onSubmit={handleSubmit} className="session-form">
      <input
        type="datetime-local"
        value={date}
        onChange={(e) => setDate(e.target.value)}
        min={minDate}
        required
      />
      <input
        type="number"
        value={hallNumber}
        onChange={(e) => setHallNumber(Number(e.target.value))}
        min={1}
        placeholder="Зал"
      />
      <button type="submit" className="btn btn-primary" disabled={mutation.isPending}>
        Додати сеанс
      </button>
    </form>
  );
}
