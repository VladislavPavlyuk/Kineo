from django.utils import timezone

from kineo.models import Session


class SessionService:

    @staticmethod
    def get_upcoming(movie_id: int | str | None = None):
        qs = Session.objects.filter(date__gte=timezone.now()).order_by("date")
        if movie_id is not None:
            try:
                qs = qs.filter(movie_id=int(movie_id))
            except (ValueError, TypeError):
                pass
        return qs
