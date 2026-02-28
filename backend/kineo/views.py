# views використовують сервіси
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import (
    StudioSerializer,
    MovieSerializer,
    SessionSerializer,
    ReviewSerializer,
)
from .services import StudioService, MovieService, SessionService, ReviewService


class StudioViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = StudioSerializer

    def get_queryset(self):
        return StudioService.get_all()


class MovieViewSet(viewsets.ModelViewSet):
    serializer_class = MovieSerializer

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
        data = {**request.data, "movie": movie.id}
        serializer = ReviewSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SessionViewSet(viewsets.ModelViewSet):
    serializer_class = SessionSerializer

    def get_queryset(self):
        movie_id = self.request.query_params.get("movie")
        return SessionService.get_upcoming(movie_id=movie_id)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        movie_id = self.request.query_params.get("movie")
        return ReviewService.get_all(movie_id=movie_id)
