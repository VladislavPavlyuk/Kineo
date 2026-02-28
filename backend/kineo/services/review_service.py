from kineo.models import Review


class ReviewService:

    @staticmethod
    def get_for_movie(movie_id: int):
        return Review.objects.filter(movie_id=movie_id)

    @staticmethod
    def get_all(movie_id: int | str | None = None):
        qs = Review.objects.all()
        if movie_id is not None:
            try:
                qs = qs.filter(movie_id=int(movie_id))
            except (ValueError, TypeError):
                pass
        return qs
