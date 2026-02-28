from django import forms
from .models import Movie, Session, Review


class MovieForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = ["title", "description", "year", "duration", "genre", "poster"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }


class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ["movie", "date", "hall_number"]
        widgets = {
            "date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["username", "text", "rating"]
        widgets = {
            "text": forms.Textarea(attrs={"rows": 3}),
            "rating": forms.Select(choices=[(i, f"{i} ★") for i in range(1, 6)]),
        }
