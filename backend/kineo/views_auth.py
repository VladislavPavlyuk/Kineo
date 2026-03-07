from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User, Group
# Готова валідація пароля від Django (довжина, схожість тощо)
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import UserProfile


class RegisterView(APIView):
    # Реєстрація доступна без авторизації
    permission_classes = [AllowAny]

    def post(self, request):
        # Беремо дані з request.data і трохи чистимо (strip прибирає пробіли по краях)
        username = request.data.get("username", "").strip()
        password = request.data.get("password", "")
        email = request.data.get("email", "").strip()

        if not username:
            return Response(
                {"username": ["This field is required"]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not password:
            return Response(
                {"password": ["This field is required"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if User.objects.filter(username=username).exists():
            return Response(
                {"username": ["User with this username already exists"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            validate_password(password)
        except ValidationError as e:
            # Якщо пароль слабкий - повертаємо список причин
            return Response(
                {"password": list(e.messages)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # create_user сам хешує пароль (не зберігається у відкритому вигляді)
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email or "",
        )
        # Нового користувача додаємо у групу Clients за замовчуванням
        clients_group, _ = Group.objects.get_or_create(name="Clients")
        user.groups.add(clients_group)
        # Одразу створюємо профіль, щоб фронт міг його читати/редагувати
        UserProfile.objects.get_or_create(user=user)

        return Response(
            {"id": user.id, "username": user.username},
            status=status.HTTP_201_CREATED,
        )
