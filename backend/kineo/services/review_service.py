from kineo.models import Review


class ReviewService:

    @staticmethod
    def get_for_movie(movie_id: int):
        # Повертаємо всі відгуки для конкретного фільму
        return Review.objects.filter(movie_id=movie_id)

    @staticmethod
    def get_all(movie_id: int | str | None = None):
        # Базовий queryset
        qs = Review.objects.all()
        if movie_id is not None:
            try:
                # movie_id може прийти як рядок з query params, тому приводимо до int
                qs = qs.filter(movie_id=int(movie_id))
            except (ValueError, TypeError):
                # Якщо id некоректний, просто повернемо всі відгуки без падіння API
                pass
        return qs
