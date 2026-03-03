# views use services
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User

from .models import UserProfile, Review
from .serializers import (
    StudioSerializer,
    MovieSerializer,
    SessionSerializer,
    ReviewSerializer,
    UserProfileSerializer,
    UserBriefSerializer,
)
from .services import StudioService, MovieService, SessionService, ReviewService
from .permissions import (
    MoviePermissions,
    SessionPermissions,
    ReviewPermissions,
    is_client,
)


class StudioViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = StudioSerializer

    def get_queryset(self):
        return StudioService.get_all()


class MovieViewSet(viewsets.ModelViewSet):
    serializer_class = MovieSerializer
    permission_classes = [MoviePermissions]

    def get_queryset(self):
        return MovieService.get_all()

    @action(detail=True, methods=["get"])
    def sessions(self, request, pk=None):
        movie = self.get_object()
        sessions = SessionService.get_upcoming(movie_id=movie.id)
        return Response(SessionSerializer(sessions, many=True).data)

    @action(detail=True, methods=["get", "post"])
    def reviews(self, request, pk=None):
        movie = self.get_object()
        if request.method == "GET":
            reviews = ReviewService.get_for_movie(movie.id)
            return Response(ReviewSerializer(reviews, many=True).data)
        if not request.user.is_authenticated or not is_client(request.user):
            return Response(
                {"detail": "Тільки клієнти можуть додавати відгуки"},
                status=status.HTTP_403_FORBIDDEN,
            )
        if Review.objects.filter(movie=movie, user=request.user).exists():
            return Response(
                {"detail": "You have already reviewed this movie"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = {**request.data, "movie": movie.id, "user": request.user.id}
        serializer = ReviewSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SessionViewSet(viewsets.ModelViewSet):
    serializer_class = SessionSerializer
    permission_classes = [SessionPermissions]

    def get_queryset(self):
        movie_id = self.request.query_params.get("movie")
        return SessionService.get_upcoming(movie_id=movie_id)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [ReviewPermissions]

    def get_queryset(self):
        movie_id = self.request.query_params.get("movie")
        return ReviewService.get_all(movie_id=movie_id)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        profile, _ = UserProfile.objects.get_or_create(user=user)
        data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "groups": list(user.groups.values_list("name", flat=True)),
            "profile": UserProfileSerializer(profile).data,
        }
        return Response(data)

    def patch(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserBriefSerializer
    permission_classes = [AllowAny]

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        profile, _ = UserProfile.objects.get_or_create(user=user)
        return Response(UserProfileSerializer(profile).data)
