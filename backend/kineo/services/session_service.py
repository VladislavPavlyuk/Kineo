from django.utils import timezone

from kineo.models import Session


class SessionService:

    @staticmethod
    def get_upcoming(movie_id: int | str | None = None):
        # Беремо тільки майбутні сеанси і сортуємо за датою
        qs = Session.objects.filter(date__gte=timezone.now()).order_by("date")
        if movie_id is not None:
            try:
                # Параметр movie часто приходить як str з URL, тому конвертуємо
                qs = qs.filter(movie_id=int(movie_id))
            except (ValueError, TypeError):
                # Некоректний параметр ігноруємо, щоб API не падало 500-кою
                pass
        return qs
