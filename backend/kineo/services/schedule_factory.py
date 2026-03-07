from datetime import timedelta
from typing import Protocol

from django.utils import timezone

from kineo.models import Studio, Movie, Session


class ScheduleDataProvider(Protocol):
    # Protocol тут як "контракт": будь-який provider має мати ці 2 методи
    def get_studios(self) -> list[tuple[str, str]]:
        ...

    def get_movies(self) -> list[tuple[str, int, int, str, str]]:
        ...


class ScheduleFactory:
    def __init__(self, data_provider: ScheduleDataProvider):
        # Залежність передаємо ззовні, щоб можна було підміняти джерело даних
        self.data_provider = data_provider

    def clear(self) -> None:
        # Чистимо у порядку Session -> Movie -> Studio, щоб не впертися у FK-зв'язки
        Session.objects.all().delete()
        Movie.objects.all().delete()
        Studio.objects.all().delete()

    def create_studios(self) -> list[Studio]:
        studios = []
        for name, country in self.data_provider.get_studios():
            studio, _ = Studio.objects.get_or_create(
                name=name, defaults={"country": country}
            )
            studios.append(studio)
        return studios

    def create_movies(self, studios: list[Studio]) -> list[Movie]:
        movies_data = self.data_provider.get_movies()
        for i, (title, year, duration, genre, director) in enumerate(movies_data):
            # Розподіляємо фільми по студіях циклічно
            studio = studios[i % len(studios)]
            Movie.objects.get_or_create(
                title=title,
                year=year,
                defaults={
                    "studio": studio,
                    "description": f"Director: {director}",
                    "duration": duration,
                    "genre": genre,
                },
            )
        return list(Movie.objects.filter(studio__in=studios))

    def create_schedule(
        self,
        movies: list[Movie],
        days: int = 7,
        slots_per_day: int = 5,
        slot_interval_hours: int = 3,
        start_hour: int = 10,
    ) -> int:
        if not movies:
            return 0

        now = timezone.now()
        start = now.replace(
            hour=start_hour, minute=0, second=0, microsecond=0
        )
        if start < now:
            # Якщо сьогоднішній стартовий час уже пройшов - починаємо з наступного дня
            start += timedelta(days=1)

        created = 0
        for day in range(days):
            day_start = start + timedelta(days=day)
            for slot in range(slots_per_day):
                session_time = day_start + timedelta(hours=slot * slot_interval_hours)
                # Рівномірно чергуємо фільми по слотах
                movie = movies[(day * slots_per_day + slot) % len(movies)]
                # Простий розподіл по залах 1..3
                hall = (slot % 3) + 1
                _, created_flag = Session.objects.get_or_create(
                    movie=movie,
                    date=session_time,
                    hall_number=hall,
                )
                if created_flag:
                    created += 1
        return created
