from datetime import timedelta
import secrets

from django.contrib.auth import authenticate
from django.utils import timezone

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from documents.models import UserSession


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):

    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(
        username=username,
        password=password
    )

    if user is None:
        return Response(
            {"error": "Invalid username or password"},
            status=status.HTTP_401_UNAUTHORIZED
        )

    token = secrets.token_hex(32)

    session = UserSession.objects.create(
        user=user,
        token=token,
        expires_at=timezone.now() + timedelta(days=1)
    )

    return Response(
        {
            "message": "Login successful",
            "token": session.token
        },
        status=status.HTTP_200_OK
    )