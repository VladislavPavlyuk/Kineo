from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User, Group
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import Movie, Session, Review, UserProfile, Booking


class MovieForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = ["title", "description", "year", "duration", "genre", "poster"]
        labels = {
            "title": "Назва",
            "description": "Опис",
            "year": "Рік",
            "duration": "Тривалість (хв)",
            "genre": "Жанр",
            "poster": "Постер",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }


class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ["date", "hall_number"]
        labels = {
            "date": "Дата та час",
            "hall_number": "Номер залу",
        }
        widgets = {
            "date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["text", "rating"]
        labels = {
            "text": "Текст відгуку",
            "rating": "Оцінка",
        }
        widgets = {
            "text": forms.Textarea(attrs={"rows": 3}),
            "rating": forms.Select(choices=[(i, f"{i} ★") for i in range(1, 6)]),
        }


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField(required=False)
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm password")

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if User.objects.filter(username=username).exists():
            raise ValidationError("User with this username already exists")
        return username

    def clean(self):
        data = super().clean()
        if data.get("password") != data.get("password2"):
            raise ValidationError({"password2": "Passwords do not match"})
        if data.get("password"):
            try:
                validate_password(data["password"])
            except ValidationError as e:
                raise ValidationError({"password": list(e.messages)})
        return data


class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Username")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")


class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["bio", "phone", "photo"]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4, "placeholder": "Де кілька слів про себе ..."}),
            "phone": forms.TextInput(attrs={"placeholder": "Залишить свій номер телефона..."}),
            "photo": forms.FileInput(),
        }
        labels = {
            "photo": "Update photo",
        }


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["tickets"]
        labels = {
            "tickets": "Кількість квитків",
        }
