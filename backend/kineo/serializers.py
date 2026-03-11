from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Studio, Movie, Session, Review, UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    # source="user.id" бере поле з пов'язаної моделі User
    # read_only=True: клієнт не може змінювати ці поля через API
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = UserProfile
        fields = ["id", "user_id", "username", "email", "bio", "phone", "photo"]
        read_only_fields = ["user_id", "username", "email"]


class UserBriefSerializer(serializers.ModelSerializer):
    # SerializerMethodField обчислюється методом get_<field_name>
    profile_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "profile_url"]

    def get_profile_url(self, obj):
        # obj - це конкретний User
        return f"/api/users/{obj.id}/"


class StudioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Studio
        fields = ["id", "name", "country"]


class MovieSerializer(serializers.ModelSerializer):
    # Віддаємо назву студії окремо, щоб на фронті не робити додатковий запит
    studio_name = serializers.CharField(source="studio.name", read_only=True)

    class Meta:
        model = Movie
        fields = [
            "id", "title", "studio", "studio_name", "description", "year",
            "duration", "genre", "poster", "created_at"
        ]
        read_only_fields = ["created_at"]


class SessionSerializer(serializers.ModelSerializer):
    # Аналогічно підтягуємо назву фільму для зручності UI
    movie_title = serializers.CharField(source="movie.title", read_only=True)

    class Meta:
        model = Session
        fields = ["id", "movie", "movie_title", "date", "hall_number"]


class ReviewSerializer(serializers.ModelSerializer):
    # Додаємо дані про автора відгуку у відповідь
    username = serializers.CharField(source="user.username", read_only=True)
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    user_profile_url = serializers.SerializerMethodField()
    user_photo = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            "id", "movie", "user", "user_id", "username", "user_profile_url",
            "user_photo", "text", "rating", "created_at"
        ]
        read_only_fields = [
            "created_at",
            "user",
            "user_id",
            "username",
            "user_profile_url",
            "user_photo",
        ]

    def get_user_profile_url(self, obj):
        # Формуємо посилання на профіль автора відгуку
        return f"/api/users/{obj.user_id}/"

    def get_user_photo(self, obj):
        profile = getattr(obj.user, "profile", None)
        if not profile or not profile.photo:
            return None
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(profile.photo.url)
        return profile.photo.url
