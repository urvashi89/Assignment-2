from django.utils import timezone
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authentication import get_authorization_header

from documents.models import UserSession


class CustomTokenAuthentication(BaseAuthentication):

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth:
            return None

        schema = auth[0].lower()
        if schema not in (b"token", b"bearer"):
            return None

        if len(auth) != 2:
            raise AuthenticationFailed("Invalid token header")

        token = auth[1].decode()

        try:
            session = UserSession.objects.select_related("user").get(
                token=token,
                expires_at__gt=timezone.now()
            )
        except UserSession.DoesNotExist:
            raise AuthenticationFailed("Invalid or expired token")

        return (session.user, session)