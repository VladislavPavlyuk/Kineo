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

from .models import Movie, Session, Review, UserProfile
from .forms import MovieForm, SessionForm, ReviewForm, RegisterForm, ProfileForm, LoginForm


def _is_staff(user):
    return user.is_authenticated and user.groups.filter(name="Staff").exists()


def _is_client(user):
    return user.is_authenticated and user.groups.filter(name="Clients").exists()


def _sqlite_unicode_lower():
    from django.db import connection
    if connection.vendor != "sqlite":
        return
    connection.ensure_connection()
    conn = getattr(connection, "connection", None)
    if conn is not None:
        conn.create_function("LOWER", 1, lambda s: s.lower() if s is not None else "")


def movie_list(request):
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
    return render(request, "kineo/movie_list.html", {"movies": movies, "search_query": q})


def movie_detail(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    sessions = movie.sessions.filter(date__gte=timezone.now()).order_by("date")
    reviews = movie.reviews.select_related("user").all()
    user_review = None
    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()
    return render(
        request,
        "kineo/movie_detail.html",
        {
            "movie": movie,
            "sessions": sessions,
            "reviews": reviews,
            "user_review": user_review,
            "is_staff": _is_staff(request.user),
            "is_client": _is_client(request.user),
        },
    )


@login_required
def movie_create(request):
    if not _is_staff(request.user):
        messages.error(request, "Access denied")
        return redirect("movie_list")
    if request.method == "POST":
        form = MovieForm(request.POST, request.FILES)
        if form.is_valid():
            movie = form.save()
            messages.success(request, "Movie added")
            return redirect("movie_detail", pk=movie.pk)
    else:
        form = MovieForm()
    return render(request, "kineo/movie_form.html", {"form": form, "is_edit": False})


@login_required
def movie_edit(request, pk):
    if not _is_staff(request.user):
        messages.error(request, "Access denied")
        return redirect("movie_list")
    movie = get_object_or_404(Movie, pk=pk)
    if request.method == "POST":
        form = MovieForm(request.POST, request.FILES, instance=movie)
        if form.is_valid():
            form.save()
            messages.success(request, "Movie updated")
            return redirect("movie_detail", pk=movie.pk)
    else:
        form = MovieForm(instance=movie)
    return render(request, "kineo/movie_form.html", {"form": form, "movie": movie, "is_edit": True})


@login_required
@require_http_methods(["POST"])
def movie_delete(request, pk):
    if not _is_staff(request.user):
        messages.error(request, "Access denied")
        return redirect("movie_list")
    movie = get_object_or_404(Movie, pk=pk)
    movie.delete()
    messages.success(request, "Movie deleted")
    return redirect("movie_list")


def sessions_list(request):
    sessions = Session.objects.filter(
        date__gte=timezone.now()
    ).select_related("movie").order_by("date")
    return render(request, "kineo/sessions_list.html", {"sessions": sessions})


@login_required
def session_create(request, movie_id):
    if not _is_staff(request.user):
        messages.error(request, "Access denied")
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
    if not _is_client(request.user):
        messages.error(request, "Only clients can add reviews")
        return redirect("movie_detail", pk=movie_id)
    movie = get_object_or_404(Movie, pk=movie_id)
    if Review.objects.filter(movie=movie, user=request.user).exists():
        messages.error(request, "You have already reviewed this movie")
        return redirect("movie_detail", pk=movie_id)
    form = ReviewForm(request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.movie = movie
        review.user = request.user
        review.save()
        messages.success(request, "Review added")
    else:
        messages.error(request, form.errors.as_text())
    return redirect("movie_detail", pk=movie_id)


@login_required
def review_edit(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if review.user_id != request.user.id:
        messages.error(request, "Access denied")
        return redirect("movie_detail", pk=review.movie_id)
    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "Review updated")
            return redirect("movie_detail", pk=review.movie_id)
    else:
        form = ReviewForm(instance=review)
    return render(request, "kineo/review_edit.html", {"form": form, "review": review})


@login_required
@require_http_methods(["POST"])
def review_delete(request, pk):
    review = get_object_or_404(Review, pk=pk)
    movie_id = review.movie_id
    if review.user_id != request.user.id and not _is_staff(request.user):
        messages.error(request, "Access denied")
        return redirect("movie_detail", pk=movie_id)
    review.delete()
    messages.success(request, "Review deleted")
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
            messages.success(request, "Registration successful")
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
    messages.success(request, "You have been logged out")
    return redirect("movie_list")


@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated")
            return redirect("profile")
    else:
        form = ProfileForm(instance=profile)
    return render(request, "kineo/profile.html", {"form": form})


def user_profile_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return render(request, "kineo/user_profile.html", {"profile": profile})
