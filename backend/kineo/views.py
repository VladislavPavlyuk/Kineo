from rest_framework import viewsets, status
# action дозволяє створювати кастомні endpoint-и всередині ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.models import User

from .models import UserProfile, Review, Booking, FavoriteMovie
from .serializers import (
    StudioSerializer,
    MovieSerializer,
    SessionSerializer,
    ReviewSerializer,
    UserProfileSerializer,
    UserBriefSerializer,
    BookingSerializer,
    FavoriteMovieSerializer,
)
from .services import StudioService, MovieService, SessionService, ReviewService
from .permissions import (
    MoviePermissions,
    SessionPermissions,
    ReviewPermissions,
    BookingPermissions,
    FavoriteMoviePermissions,
    is_client,
)


class StudioViewSet(viewsets.ReadOnlyModelViewSet):
    # ReadOnlyModelViewSet: доступні тільки list/retrieve (без create/update/delete)
    serializer_class = StudioSerializer

    def get_queryset(self):
        return StudioService.get_all()


class MovieViewSet(viewsets.ModelViewSet):
    # ModelViewSet дає повний CRUD, а хто що може робити - у permission_classes
    serializer_class = MovieSerializer
    permission_classes = [MoviePermissions]

    def get_queryset(self):
        return MovieService.get_all()

    @action(detail=True, methods=["get"])
    def sessions(self, request, pk=None):
        # detail=True означає маршрут виду /movies/<id>/sessions/
        movie = self.get_object()
        sessions = SessionService.get_upcoming(movie_id=movie.id)
        return Response(SessionSerializer(sessions, many=True).data)

    @action(detail=True, methods=["get", "post"])
    def reviews(self, request, pk=None):
        movie = self.get_object()
        if request.method == "GET":
            reviews = ReviewService.get_for_movie(movie.id)
            return Response(
                ReviewSerializer(reviews, many=True, context={"request": request}).data
            )
        # Додавати відгук може тільки авторизований користувач з роллю client
        if not request.user.is_authenticated or not is_client(request.user):
            return Response(
                {"detail": "Тільки клієнти можуть додавати відгуки"},
                status=status.HTTP_403_FORBIDDEN,
            )
        # Не даємо створити другий відгук на той самий фільм
        if Review.objects.filter(movie=movie, user=request.user).exists():
            return Response(
                {"detail": "You have already reviewed this movie"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Беремо дані з request, але movie/user підставляємо з бекенду для безпеки
        UserProfile.objects.get_or_create(user=request.user)
        data = {**request.data, "movie": movie.id, "user": request.user.id}
        serializer = ReviewSerializer(data=data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SessionViewSet(viewsets.ModelViewSet):
    serializer_class = SessionSerializer
    permission_classes = [SessionPermissions]

    def get_queryset(self):
        # Якщо movie є в query params, повертаємо сеанси лише для цього фільму
        movie_id = self.request.query_params.get("movie")
        return SessionService.get_upcoming(movie_id=movie_id)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [ReviewPermissions]

    def get_queryset(self):
        # Тут така сама фільтрація по movie, як і для сеансів
        movie_id = self.request.query_params.get("movie")
        return ReviewService.get_all(movie_id=movie_id)


class MeView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        user = request.user
        # Створюємо профіль автоматично, якщо користувач зайшов вперше
        profile, _ = UserProfile.objects.get_or_create(user=user)
        # Формуємо відповідь вручну, щоб повернути і user, і profile в одному JSON
        data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "groups": list(user.groups.values_list("name", flat=True)),
            "profile": UserProfileSerializer(profile, context={"request": request}).data,
        }
        return Response(data)

    def patch(self, request):
        # Та сама ідея: перед оновленням профіль має існувати
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                UserProfileSerializer(profile, context={"request": request}).data
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserBriefSerializer
    permission_classes = [AllowAny]

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        profile, _ = UserProfile.objects.get_or_create(user=user)
        return Response(UserProfileSerializer(profile, context={"request": request}).data)


class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [BookingPermissions]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).select_related(
            "session", "session__movie"
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FavoriteMovieViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteMovieSerializer
    permission_classes = [FavoriteMoviePermissions]
    http_method_names = ["get", "post", "head", "delete"]

    def get_queryset(self):
        return FavoriteMovie.objects.filter(user=self.request.user).select_related(
            "movie"
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
