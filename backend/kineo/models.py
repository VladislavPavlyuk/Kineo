import os

from django.conf import settings
from django.db import models
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
import os


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    photo = models.ImageField(upload_to="profile_photos/", blank=True, null=True)

    def __str__(self):
        return str(self.user)


class Studio(models.Model):
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=100, default="Ukraine")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Hall(models.Model):
    name = models.CharField(max_length=255)
    seats = models.PositiveIntegerField(default=50)

    class Meta:
        ordering = ["name"]
        verbose_name = "Зал"
        verbose_name_plural = "Зали"

    def __str__(self):
        return f"{self.name} ({self.seats} місць)"


class Movie(models.Model):
    title = models.CharField(max_length=255)
    studio = models.ForeignKey(
        Studio, on_delete=models.SET_NULL, null=True, blank=True, related_name="movies"
    )
    description = models.TextField(blank=True)
    year = models.PositiveIntegerField()
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    genre = models.CharField(max_length=100)
    poster = models.ImageField(upload_to="posters/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-year", "title"]

    def __str__(self):
        return f"{self.title} ({self.year})"


class Session(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="sessions")
    date = models.DateTimeField()
    hall_number = models.PositiveIntegerField()

    class Meta:
        ordering = ["date"]

    def __str__(self):
        return f"{self.movie.title} - {self.date}"


class Review(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews"
    )
    text = models.TextField()
    rating = models.PositiveSmallIntegerField(default=5)  # 1 to 5
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = [["movie", "user"]]

    def __str__(self):
        return f"{self.user} - {self.movie.title}"


class Booking(models.Model):
    session = models.ForeignKey(
        Session, on_delete=models.CASCADE, related_name="bookings"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings"
    )
    tickets = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} – {self.session} ({self.tickets})"


class FavoriteMovie(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favorite_movies"
    )
    movie = models.ForeignKey(
        Movie, on_delete=models.CASCADE, related_name="favorited_by"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [["user", "movie"]]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} ❤ {self.movie}"


def _is_profile_photo(file_field):
    if not file_field or not file_field.name:
        return False
    normalized = file_field.name.replace("\\", "/")
    return normalized.startswith("profile_photos/")


def _delete_file(file_field):
    if not file_field or not file_field.path:
        return
    if os.path.exists(file_field.path):
        os.remove(file_field.path)


@receiver(post_delete, sender=UserProfile)
def delete_profile_photo_on_delete(sender, instance, **kwargs):
    if _is_profile_photo(instance.photo):
        _delete_file(instance.photo)


@receiver(pre_save, sender=UserProfile)
def delete_profile_photo_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old = UserProfile.objects.get(pk=instance.pk)
    except UserProfile.DoesNotExist:
        return
    if not old.photo:
        return
    if old.photo == instance.photo:
        return
    if _is_profile_photo(old.photo):
        _delete_file(old.photo)
