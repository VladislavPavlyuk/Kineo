from rest_framework import serializers
from .models import Studio, Movie, Session, Review


class StudioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Studio
        fields = ["id", "name", "country"]


class MovieSerializer(serializers.ModelSerializer):
    studio_name = serializers.CharField(source="studio.name", read_only=True)

    class Meta:
        model = Movie
        fields = [
            "id", "title", "studio", "studio_name", "description", "year",
            "duration", "genre", "poster", "created_at"
        ]
        read_only_fields = ["created_at"]


class SessionSerializer(serializers.ModelSerializer):
    movie_title = serializers.CharField(source="movie.title", read_only=True)

    class Meta:
        model = Session
        fields = ["id", "movie", "movie_title", "date", "hall_number"]


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["id", "movie", "username", "text", "rating", "created_at"]
        read_only_fields = ["created_at"]
