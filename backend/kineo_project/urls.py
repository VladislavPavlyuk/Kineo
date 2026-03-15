from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from kineo.views import (
    StudioViewSet,
    MovieViewSet,
    SessionViewSet,
    ReviewViewSet,
    UserProfileViewSet,
    MeView,
    BookingViewSet,
    FavoriteMovieViewSet,
)
from kineo.views_auth import RegisterView
from kineo.views_web import (
    movie_list,
    movie_detail,
    movie_create,
    movie_edit,
    movie_delete,
    sessions_list,
    schedule_generate,
    schedule_plan,
    hall_list,
    hall_create,
    hall_edit,
    hall_delete,
    session_book,
    session_create,
    session_edit,
    session_delete,
    review_create,
    review_edit,
    review_delete,
    register_view,
    profile_view,
    user_profile_view,
    logout_view,
    client_cabinet,
    my_bookings,
    booking_update,
    booking_delete,
    bookings_pay,
    favorite_toggle,
    my_favorites,
    movie_book,
)
from kineo.views_web import KineoLoginView

router = DefaultRouter()
router.register("studios", StudioViewSet, basename="studio")
router.register("movies", MovieViewSet, basename="movie")
router.register("sessions", SessionViewSet, basename="session")
router.register("reviews", ReviewViewSet, basename="review")
router.register("users", UserProfileViewSet, basename="user")
router.register("bookings", BookingViewSet, basename="booking")
router.register("favorites", FavoriteMovieViewSet, basename="favoritemovie")

urlpatterns = [
    path("favicon.ico", RedirectView.as_view(url="/static/kineo/favicon.ico", permanent=True)),
    path("", movie_list, name="movie_list"),
    path("admin/", admin.site.urls),
    path("movies/", movie_list),
    path("movies/new/", movie_create, name="movie_create"),
    path("movies/<int:pk>/", movie_detail, name="movie_detail"),
    path("movies/<int:pk>/edit/", movie_edit, name="movie_edit"),
    path("movies/<int:pk>/delete/", movie_delete, name="movie_delete"),
    path("movies/<int:pk>/book/", movie_book, name="movie_book"),
    path("sessions/", sessions_list, name="sessions_list"),
    path("sessions/generate/", schedule_generate, name="schedule_generate"),
    path("sessions/plan/", schedule_plan, name="schedule_plan"),
    path("halls/", hall_list, name="hall_list"),
    path("halls/new/", hall_create, name="hall_create"),
    path("halls/<int:pk>/edit/", hall_edit, name="hall_edit"),
    path("halls/<int:pk>/delete/", hall_delete, name="hall_delete"),
    path("sessions/<int:session_id>/book/", session_book, name="session_book"),
    path("sessions/<int:pk>/edit/", session_edit, name="session_edit"),
    path("sessions/<int:pk>/delete/", session_delete, name="session_delete"),
    path("movies/<int:movie_id>/sessions/new/", session_create, name="session_create"),
    path("movies/<int:movie_id>/reviews/", review_create, name="review_create"),
    path("reviews/<int:pk>/edit/", review_edit, name="review_edit"),
    path("reviews/<int:pk>/delete/", review_delete, name="review_delete"),
    path("login/", KineoLoginView.as_view(), name="login"),
    path("logout/", logout_view, name="logout"),
    path("register/", register_view, name="register"),
    path("profile/", profile_view, name="profile"),
    path("cabinet/", client_cabinet, name="client_cabinet"),
    path("bookings/", my_bookings, name="my_bookings"),
    path("bookings/<int:booking_id>/edit/", booking_update, name="booking_update"),
    path("bookings/<int:booking_id>/delete/", booking_delete, name="booking_delete"),
    path("bookings/pay/", bookings_pay, name="bookings_pay"),
    path("movies/<int:movie_id>/favorite-toggle/", favorite_toggle, name="favorite_toggle"),
    path("favorites/", my_favorites, name="my_favorites"),
    path("users/<int:pk>/", user_profile_view, name="user_profile"),
    path("api/auth/token/", TokenObtainPairView.as_view()),
    path("api/auth/token/refresh/", TokenRefreshView.as_view()),
    path("api/auth/register/", RegisterView.as_view()),
    path("api/auth/me/", MeView.as_view()),
    path("api/", include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
