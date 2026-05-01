"""Account create / verify email / me endpoints."""

from __future__ import annotations

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_api_key.permissions import HasAPIKey

from accounts.api.v1.serializers.user import UserCreateSerializer, UserSerializer

User = get_user_model()


class AccountCreateView(generics.CreateAPIView):
    """POST /api/v1/auth/account/create/   Sign up with email+password."""

    serializer_class = UserCreateSerializer
    permission_classes = [HasAPIKey]
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.save()

        if getattr(settings, "ACCOUNT_VERIFY_EMAIL_REQUIRED", False):
            user.is_active = False
            user.save(update_fields=["is_active"])
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            verify_url = (
                f"/api/v1/auth/account/verify/{uidb64}/{token}/"
            )
            try:
                send_mail(
                    subject="Verifica tu cuenta PlayBook",
                    message=f"Verifica tu cuenta abriendo: {verify_url}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
            except Exception:
                pass
            return Response({"detail": "check your email"}, status=status.HTTP_201_CREATED)

        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class AccountVerifyEmailView(APIView):
    """GET /api/v1/auth/account/verify/<uidb64>/<token>/"""

    permission_classes = [HasAPIKey]
    authentication_classes = []

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"detail": "invalid"}, status=400)
        if not default_token_generator.check_token(user, token):
            return Response({"detail": "invalid_or_expired"}, status=400)
        user.is_active = True
        user.save(update_fields=["is_active"])
        return Response(UserSerializer(user).data)


class AccountMeView(APIView):
    """GET /api/v1/auth/account/me/                — current user info
    PUT /api/v1/auth/account/me/                — change password
       body: {current_password, new_password}
    """

    permission_classes = [IsAuthenticated, HasAPIKey]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def put(self, request):
        cur = request.data.get("current_password")
        new = request.data.get("new_password")
        if not cur or not new:
            return Response({"detail": "missing fields"}, status=400)
        if not request.user.check_password(cur):
            return Response({"detail": "wrong current password"}, status=400)
        request.user.set_password(new)
        request.user.save()
        return Response(status=200)
