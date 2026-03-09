from datetime import timedelta

from django.db.models import Max
from django.utils import timezone

from kineo.models import Movie, Session


def get_num_halls():
    r = Session.objects.aggregate(Max("hall_number"))
    return r["hall_number__max"] or 3


def generate_month_schedule():
    movies = list(Movie.objects.all())
    if not movies:
        return 0
    num_halls = get_num_halls()
    now = timezone.now()
    start = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=3)
    created = 0
    movie_index = 0
    day = start
    while day < end:
        weekday = day.weekday()
        is_weekend = weekday >= 5

        if not is_weekend:
            for hour in range(10, 18):
                slot = day.replace(hour=hour, minute=0, second=0, microsecond=0)
                if slot >= now:
                    for hall in range(1, num_halls + 1):
                        _, created_flag = Session.objects.get_or_create(
                            date=slot,
                            hall_number=hall,
                            defaults={"movie_id": movies[movie_index % len(movies)].pk},
                        )
                        if created_flag:
                            created += 1
                        movie_index += 1

        if is_weekend:
            for minute_offset in range(0, 12 * 60, 20):
                slot = day.replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(
                    minutes=minute_offset
                )
                if slot.date() != day.date():
                    break
                if slot >= now:
                    for hall in range(1, num_halls + 1):
                        _, created_flag = Session.objects.get_or_create(
                            date=slot,
                            hall_number=hall,
                            defaults={"movie_id": movies[movie_index % len(movies)].pk},
                        )
                        if created_flag:
                            created += 1
                        movie_index += 1

        for minute_offset in range(0, 5 * 60, 15):
            slot = day.replace(hour=18, minute=0, second=0, microsecond=0) + timedelta(
                minutes=minute_offset
            )
            if slot.date() != day.date():
                break
            if slot >= now:
                for hall in range(1, num_halls + 1):
                    _, created_flag = Session.objects.get_or_create(
                        date=slot,
                        hall_number=hall,
                        defaults={"movie_id": movies[movie_index % len(movies)].pk},
                    )
                    if created_flag:
                        created += 1
                    movie_index += 1

        day += timedelta(days=1)
    return created
