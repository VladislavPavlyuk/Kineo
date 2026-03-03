from django.contrib import admin
from .models import UserProfile, Studio, Movie, Session, Review


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "phone"]




@admin.register(Studio)
class StudioAdmin(admin.ModelAdmin):
    list_display = ["name", "country"]


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ["title", "studio", "year", "genre", "duration"]


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ["movie", "date", "hall_number"]
    list_filter = ["date"]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["user", "movie", "rating", "created_at"]
