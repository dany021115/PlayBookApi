from rest_framework import serializers

from accounts.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(allow_blank=True, allow_null=True, required=False)

    class Meta:
        model = Profile
        fields = ["id", "avatar", "phone", "country", "provider", "locale"]
        read_only_fields = ["id", "provider"]
