from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User, Group
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import UserProfile


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username", "").strip()
        password = request.data.get("password", "")
        email = request.data.get("email", "").strip()

        if not username:
            return Response(
                {"username": ["Обов'язкове поле"]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not password:
            return Response(
                {"password": ["Обов'язкове поле"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if User.objects.filter(username=username).exists():
            return Response(
                {"username": ["Користувач з таким ім'ям вже існує"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            validate_password(password)
        except ValidationError as e:
            return Response(
                {"password": list(e.messages)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email or "",
        )
        clients_group, _ = Group.objects.get_or_create(name="Clients")
        user.groups.add(clients_group)
        UserProfile.objects.get_or_create(user=user)

        return Response(
            {"id": user.id, "username": user.username},
            status=status.HTTP_201_CREATED,
        )
