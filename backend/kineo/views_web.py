from django.db.models import Q
from django.db.models.functions import Lower
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User, Group
from django.conf import settings
from django.urls import reverse
import os

from .models import Movie, Session, Review, UserProfile, Studio, Booking, FavoriteMovie, Hall
from .forms import (
    MovieForm,
    SessionForm,
    ReviewForm,
    RegisterForm,
    ProfileForm,
    LoginForm,
    BookingForm,
    HallForm,
)
from .permissions import is_staff, is_client
from .services.schedule_generator import generate_month_schedule, plan_week_schedule


def _sqlite_unicode_lower():
    from django.db import connection
    if connection.vendor != "sqlite":
        return
    connection.ensure_connection()
    conn = getattr(connection, "connection", None)
    if conn is not None:
        conn.create_function("LOWER", 1, lambda s: s.lower() if s is not None else "")


def _get_navbar_filter_options():
    genres = list(Movie.objects.values_list("genre", flat=True).distinct().order_by("genre"))
    studios = list(Studio.objects.all())
    years = list(Movie.objects.values_list("year", flat=True).distinct().order_by("-year"))
    return {"genres": genres, "studios": studios, "years": years}


def _get_avatar_library():
    avatars_dir = os.path.join(settings.MEDIA_ROOT, "avatars")
    if not os.path.isdir(avatars_dir):
        return []
    allowed_ext = (".png", ".jpg", ".jpeg", ".webp", ".gif")
    avatars = []
    for filename in sorted(os.listdir(avatars_dir)):
        if filename.lower().endswith(allowed_ext):
            avatars.append(
                {
                    "name": filename,
                    "url": f"{settings.MEDIA_URL}avatars/{filename}",
                }
            )
    return avatars


def _get_movie_filter_queryset(request):
    movies = Movie.objects.all()
    q = request.GET.get("q", "").strip()
    if q:
        _sqlite_unicode_lower()
        q_lo = q.lower()
        movies = movies.annotate(
            _title_lo=Lower("title"),
            _desc_lo=Lower("description"),
            _genre_lo=Lower("genre"),
            _studio_lo=Lower("studio__name"),
        )
        q_filter = (
            Q(_title_lo__contains=q_lo)
            | Q(_desc_lo__contains=q_lo)
            | Q(_genre_lo__contains=q_lo)
            | Q(_studio_lo__contains=q_lo)
        )
        if len(q) == 4 and q.isdigit():
            q_filter |= Q(year=int(q))
        movies = movies.filter(q_filter)
    year = request.GET.get("year", "").strip()
    if year and year.isdigit():
        movies = movies.filter(year=int(year))
    genre = request.GET.get("genre", "").strip()
    if genre:
        movies = movies.filter(genre__iexact=genre)
    studio_id = request.GET.get("studio", "").strip()
    if studio_id and studio_id.isdigit():
        movies = movies.filter(studio_id=int(studio_id))
    duration_min = request.GET.get("duration_min", "").strip()
    if duration_min and duration_min.isdigit():
        movies = movies.filter(duration__gte=int(duration_min))
    duration_max = request.GET.get("duration_max", "").strip()
    if duration_max and duration_max.isdigit():
        movies = movies.filter(duration__lte=int(duration_max))
    return movies


def movie_list(request):
    movies = _get_movie_filter_queryset(request)
    return render(
        request,
        "kineo/movie_list.html",
        {
            "movies": movies,
            "search_query": request.GET.get("q", "").strip(),
            "navbar_filter_options": _get_navbar_filter_options(),
        },
    )


def movie_detail(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    sessions = movie.sessions.filter(date__gte=timezone.now()).order_by("date")
    reviews = movie.reviews.select_related("user").all()
    reviewer_ids = list(reviews.values_list("user_id", flat=True))
    if reviewer_ids:
        existing_profiles = set(
            UserProfile.objects.filter(user_id__in=reviewer_ids).values_list("user_id", flat=True)
        )
        missing_ids = [uid for uid in reviewer_ids if uid not in existing_profiles]
        if missing_ids:
            UserProfile.objects.bulk_create(
                [UserProfile(user_id=uid) for uid in missing_ids],
                ignore_conflicts=True,
            )
    reviews = movie.reviews.select_related("user", "user__profile").all()
    user_review = None
    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()
        is_favorite = FavoriteMovie.objects.filter(
            user=request.user, movie=movie
        ).exists()
    else:
        is_favorite = False
    return render(
        request,
        "kineo/movie_detail.html",
        {
            "movie": movie,
            "sessions": sessions,
            "reviews": reviews,
            "user_review": user_review,
            "is_staff": is_staff(request.user),
            "is_client": is_client(request.user),
            "is_favorite": is_favorite,
        },
    )


@login_required
def movie_create(request):
    if not is_staff(request.user):
        messages.error(request, "Доступ заборонено")
        return redirect("movie_list")
    if request.method == "POST":
        form = MovieForm(request.POST, request.FILES)
        if form.is_valid():
            movie = form.save()
            messages.success(request, "Фільм додано")
            return redirect("movie_detail", pk=movie.pk)
    else:
        form = MovieForm()
    return render(request, "kineo/movie_form.html", {"form": form, "is_edit": False})


@login_required
def movie_edit(request, pk):
    if not is_staff(request.user):
        messages.error(request, "Доступ заборонено")
        return redirect("movie_list")
    movie = get_object_or_404(Movie, pk=pk)
    if request.method == "POST":
        form = MovieForm(request.POST, request.FILES, instance=movie)
        if form.is_valid():
            form.save()
            messages.success(request, "Фільм оновлено")
            return redirect("movie_detail", pk=movie.pk)
    else:
        form = MovieForm(instance=movie)
    return render(request, "kineo/movie_form.html", {"form": form, "movie": movie, "is_edit": True})


@login_required
@require_http_methods(["POST"])
def movie_delete(request, pk):
    if not is_staff(request.user):
        messages.error(request, "Доступ заборонено")
        return redirect("movie_list")
    movie = get_object_or_404(Movie, pk=pk)
    movie.delete()
    messages.success(request, "Фільм видалено")
    return redirect("movie_list")


def sessions_list(request):
    movies_filtered = _get_movie_filter_queryset(request)
    sessions = Session.objects.filter(
        date__gte=timezone.now(),
        movie__in=movies_filtered,
    ).select_related("movie")
    movie_param = request.GET.get("movie")
    if movie_param and movie_param.isdigit():
        sessions = sessions.filter(movie_id=int(movie_param))
    sessions = sessions.order_by("date")
    return render(
        request,
        "kineo/sessions_list.html",
        {
            "sessions": sessions,
            "is_staff": is_staff(request.user),
            "navbar_filter_options": _get_navbar_filter_options(),
        },
    )


@login_required
def movie_book(request, pk):
    url = f"{reverse('sessions_list')}?movie={pk}"
    return redirect(url)


@login_required
def client_cabinet(request):
    if not is_client(request.user):
        messages.error(request, "Особистий кабінет доступний лише для клієнтів")
        return redirect("movie_list")
    reviews = (
        Review.objects.filter(user=request.user)
        .select_related("movie")
        .order_by("-created_at")
    )
    viewed_movies = (
        Movie.objects.filter(sessions__bookings__user=request.user)
        .distinct()
        .order_by("-sessions__date")
    )
    favorites = (
        Movie.objects.filter(favorited_by__user=request.user)
        .distinct()
        .order_by("title")
    )
    stats = {
        "reviews_count": reviews.count(),
        "viewed_count": viewed_movies.count(),
        "favorites_count": favorites.count(),
        "bookings_count": Booking.objects.filter(user=request.user).count(),
    }
    return render(
        request,
        "kineo/client_cabinet.html",
        {
            "reviews": reviews,
            "viewed_movies": viewed_movies,
            "favorites": favorites,
            "stats": stats,
        },
    )


@login_required
def my_bookings(request):
    if not is_client(request.user):
        messages.error(request, "Тільки клієнти мають сторінку бронювань")
        return redirect("sessions_list")
    bookings = (
        Booking.objects.filter(user=request.user)
        .select_related("session__movie")
        .order_by("-created_at")
    )
    return render(
        request,
        "kineo/my_bookings.html",
        {"bookings": bookings},
    )


@login_required
@require_http_methods(["POST"])
def session_book(request, session_id):
    # Дозволяємо бронювання лише клієнтам.
    if not is_client(request.user):
        messages.error(request, "Тільки клієнти можуть бронювати квитки")
        return redirect("sessions_list")
    session = get_object_or_404(Session, pk=session_id)
    form = BookingForm(request.POST)
    if form.is_valid():
        booking = form.save(commit=False)
        booking.session = session
        booking.user = request.user
        booking.save()
        messages.success(
            request,
            f"Бронювання створено: {session.movie.title}, "
            f"{session.date:%d.%m %H:%M} — {booking.tickets} квитків.",
        )
    else:
        messages.error(request, "Невірна кількість квитків. Введіть число від 1 до 10.")
    return redirect("sessions_list")


@login_required
@require_http_methods(["POST"])
def booking_update(request, booking_id):
    if not is_client(request.user):
        messages.error(request, "Тільки клієнти можуть змінювати бронювання")
        return redirect("my_bookings")
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    form = BookingForm(request.POST, instance=booking)
    if form.is_valid():
        form.save()
        messages.success(request, "Бронювання оновлено")
    else:
        messages.error(request, "Невірна кількість квитків. Введіть число від 1 до 10.")
    return redirect("my_bookings")


@login_required
@require_http_methods(["POST"])
def booking_delete(request, booking_id):
    if not is_client(request.user):
        messages.error(request, "Тільки клієнти можуть видаляти бронювання")
        return redirect("my_bookings")
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    booking.delete()
    messages.success(request, "Бронювання видалено")
    return redirect("my_bookings")


@login_required
@require_http_methods(["POST"])
def bookings_pay(request):
    if not is_client(request.user):
        messages.error(request, "Тільки клієнти можуть сплачувати бронювання")
        return redirect("sessions_list")
    has_any = Booking.objects.filter(user=request.user).exists()
    if not has_any:
        messages.error(request, "Немає бронювань для оплати")
        return redirect("my_bookings")
    # Тут могла б бути інтеграція з платіжною системою.
    messages.success(request, "Оплата успішна (демо).")
    return redirect("my_bookings")


@login_required
@require_http_methods(["POST"])
def favorite_toggle(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    fav_qs = FavoriteMovie.objects.filter(user=request.user, movie=movie)
    if fav_qs.exists():
        fav_qs.delete()
        messages.success(request, "Фільм видалено з улюблених")
    else:
        FavoriteMovie.objects.get_or_create(user=request.user, movie=movie)
        messages.success(request, "Фільм додано до улюблених")
    return redirect("movie_detail", pk=movie_id)


@login_required
def my_favorites(request):
    movies = (
        Movie.objects.filter(favorited_by__user=request.user)
        .distinct()
        .order_by("title")
    )
    return render(
        request,
        "kineo/my_favorites.html",
        {"movies": movies},
    )


@login_required
@require_http_methods(["POST"])
def schedule_generate(request):
    if not is_staff(request.user):
        messages.error(request, "Доступ заборонено")
        return redirect("sessions_list")
    created = generate_month_schedule()
    messages.success(request, f"Розклад згенеровано. Додано сеансів: {created}.")
    return redirect("sessions_list")


@login_required
def schedule_plan(request):
    if not is_staff(request.user):
        messages.error(request, "Доступ заборонено")
        return redirect("movie_list")
    if request.method == "POST":
        created = plan_week_schedule()
        messages.success(
            request,
            f"Розклад на наступний тиждень заплановано. Додано сеансів: {created}.",
        )
        return redirect("sessions_list")
    return render(request, "kineo/schedule_plan.html")


def _hall_staff_redirect(request):
    if not request.user.is_authenticated or not is_staff(request.user):
        messages.error(request, "Доступ заборонено")
        return redirect("movie_list")
    return None


@login_required
def hall_list(request):
    if (r := _hall_staff_redirect(request)):
        return r
    halls = Hall.objects.all()
    return render(request, "kineo/hall_list.html", {"halls": halls})


@login_required
def hall_create(request):
    if (r := _hall_staff_redirect(request)):
        return r
    if request.method == "POST":
        form = HallForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Зал додано")
            return redirect("hall_list")
    else:
        form = HallForm()
    return render(request, "kineo/hall_form.html", {"form": form, "hall": None, "is_edit": False})


@login_required
def hall_edit(request, pk):
    if (r := _hall_staff_redirect(request)):
        return r
    hall = get_object_or_404(Hall, pk=pk)
    if request.method == "POST":
        form = HallForm(request.POST, instance=hall)
        if form.is_valid():
            form.save()
            messages.success(request, "Зал оновлено")
            return redirect("hall_list")
    else:
        form = HallForm(instance=hall)
    return render(request, "kineo/hall_form.html", {"form": form, "hall": hall, "is_edit": True})


@login_required
@require_http_methods(["POST"])
def hall_delete(request, pk):
    if (r := _hall_staff_redirect(request)):
        return r
    hall = get_object_or_404(Hall, pk=pk)
    hall.delete()
    messages.success(request, "Зал видалено")
    return redirect("hall_list")


@login_required
def session_create(request, movie_id):
    if not is_staff(request.user):
        messages.error(request, "Доступ заборонено")
        return redirect("movie_list")
    movie = get_object_or_404(Movie, pk=movie_id)
    if request.method == "POST":
        form = SessionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.movie = movie
            session.save()
            messages.success(request, "Сеанс додано")
            return redirect("movie_detail", pk=movie_id)
    else:
        form = SessionForm()
    return render(request, "kineo/session_form.html", {"form": form, "movie": movie})


@login_required
@require_http_methods(["POST"])
def review_create(request, movie_id):
    if not is_client(request.user):
        messages.error(request, "Додавати відгуки можуть лише клієнти")
        return redirect("movie_detail", pk=movie_id)
    movie = get_object_or_404(Movie, pk=movie_id)
    if Review.objects.filter(movie=movie, user=request.user).exists():
        messages.error(request, "Ви вже залишали відгук на цей фільм")
        return redirect("movie_detail", pk=movie_id)
    UserProfile.objects.get_or_create(user=request.user)
    form = ReviewForm(request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.movie = movie
        review.user = request.user
        review.save()
        messages.success(request, "Відгук додано")
    else:
        messages.error(request, form.errors.as_text())
    return redirect("movie_detail", pk=movie_id)


@login_required
def review_edit(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if review.user_id != request.user.id:
        messages.error(request, "Доступ заборонено")
        return redirect("movie_detail", pk=review.movie_id)
    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "Відгук оновлено")
            return redirect("movie_detail", pk=review.movie_id)
    else:
        form = ReviewForm(instance=review)
    return render(request, "kineo/review_edit.html", {"form": form, "review": review})


@login_required
@require_http_methods(["POST"])
def review_delete(request, pk):
    review = get_object_or_404(Review, pk=pk)
    movie_id = review.movie_id
    if review.user_id != request.user.id and not is_staff(request.user):
        messages.error(request, "Доступ заборонено")
        return redirect("movie_detail", pk=movie_id)
    review.delete()
    messages.success(request, "Відгук видалено")
    return redirect("movie_detail", pk=movie_id)


def register_view(request):
    if request.user.is_authenticated:
        return redirect("movie_list")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data["username"].strip(),
                password=form.cleaned_data["password"],
                email=form.cleaned_data.get("email", ""),
            )
            clients, _ = Group.objects.get_or_create(name="Clients")
            user.groups.add(clients)
            UserProfile.objects.get_or_create(user=user)
            login(request, user)
            messages.success(request, "Реєстрація успішна")
            return redirect("movie_list")
    else:
        form = RegisterForm()
    return render(request, "kineo/register.html", {"form": form})


class KineoLoginView(LoginView):
    template_name = "kineo/login.html"
    redirect_authenticated_user = True
    authentication_form = LoginForm


def logout_view(request):
    logout(request)
    messages.success(request, "Ви вийшли з облікового запису")
    return redirect("movie_list")


@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    avatars = _get_avatar_library()
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        if username:
            if username != request.user.username and User.objects.filter(username=username).exists():
                messages.error(request, "Користувач з таким іменем вже існує")
                form = ProfileForm(instance=profile)
                return render(request, "kineo/profile.html", {"form": form, "avatars": avatars})
            if username != request.user.username:
                request.user.username = username
                request.user.save(update_fields=["username"])
        avatar_filename = request.POST.get("avatar_filename", "").strip()
        if avatar_filename:
            avatar_names = {avatar["name"] for avatar in avatars}
            if avatar_filename in avatar_names:
                profile.photo.name = f"avatars/{avatar_filename}"
                profile.save(update_fields=["photo"])
                messages.success(request, "Аватар оновлено")
                return redirect("profile")
            messages.error(request, "Невірний вибір аватара")
            form = ProfileForm(instance=profile)
            return render(request, "kineo/profile.html", {"form": form, "avatars": avatars})
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Профіль оновлено")
            return redirect("profile")
    else:
        form = ProfileForm(instance=profile)
    return render(request, "kineo/profile.html", {"form": form, "avatars": avatars})


def user_profile_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return render(request, "kineo/user_profile.html", {"profile": profile})
