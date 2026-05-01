from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_api_key.permissions import HasAPIKey

from notifications.api.v1.serializers import DeviceTokenSerializer
from notifications.models import DeviceToken


class DeviceRegisterView(APIView):
    """POST /api/v1/devices/register/  body: {token, platform: ios|android|web}"""

    permission_classes = [IsAuthenticated, HasAPIKey]

    def post(self, request):
        token = (request.data.get("token") or "").strip()
        platform = (request.data.get("platform") or "android").lower()
        if not token:
            return Response({"detail": "missing_token"}, status=status.HTTP_400_BAD_REQUEST)
        obj, _ = DeviceToken.objects.update_or_create(
            token=token,
            defaults={"user": request.user, "platform": platform, "active": True},
        )
        return Response(DeviceTokenSerializer(obj).data, status=status.HTTP_200_OK)
