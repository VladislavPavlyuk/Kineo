from datetime import datetime, time, timedelta

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


def plan_week_schedule():
    """
    Планує сеанси на тиждень, що починається наступного дня після останнього
    дня існуючого розкладу. Рівномірно розподіляє всі фільми по слотах.
    """
    movies = list(Movie.objects.all())
    if not movies:
        return 0
    num_halls = get_num_halls()
    last = Session.objects.aggregate(Max("date"))["date__max"]
    if last:
        first_plan_date = last.date() + timedelta(days=1)
    else:
        first_plan_date = (timezone.now() + timedelta(days=1)).date()
    tz = timezone.get_current_timezone()
    created = 0
    movie_index = 0
    for day_offset in range(7):
        current_date = first_plan_date + timedelta(days=day_offset)
        start_of_day = timezone.make_aware(
            datetime.combine(current_date, time(0, 0)), tz
        )
        is_weekend = current_date.weekday() >= 5
        slots = []
        if is_weekend:
            for minute_offset in range(0, 13 * 60, 30):
                slot = start_of_day.replace(
                    hour=9, minute=0, second=0, microsecond=0
                ) + timedelta(minutes=minute_offset)
                if slot.date() != current_date:
                    break
                for hall in range(1, num_halls + 1):
                    slots.append((slot, hall))
        else:
            for hour in range(10, 22):
                slot = start_of_day.replace(
                    hour=hour, minute=0, second=0, microsecond=0
                )
                for hall in range(1, num_halls + 1):
                    slots.append((slot, hall))
        for slot_dt, hall in slots:
            _, created_flag = Session.objects.get_or_create(
                date=slot_dt,
                hall_number=hall,
                defaults={"movie_id": movies[movie_index % len(movies)].pk},
            )
            if created_flag:
                created += 1
            movie_index += 1
    return created
