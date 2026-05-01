from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_api_key.permissions import HasAPIKey

from accounts.api.v1.serializers.profile import ProfileSerializer
from accounts.models import Profile


class MeProfileView(generics.RetrieveUpdateAPIView):
    """GET /PUT /api/v1/auth/account/me/profile/"""

    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, HasAPIKey]

    def get_object(self):
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        return profile
