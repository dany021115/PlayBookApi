from django.contrib.auth import get_user_model
from rest_framework import serializers

from accounts.api.v1.serializers.profile import ProfileSerializer
from accounts.models import Profile

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_staff",
            "is_superuser",
            "profile",
        ]
        read_only_fields = ["id", "username", "is_staff", "is_superuser"]


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    provider = serializers.CharField(write_only=True, required=False, default="password")

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "first_name", "last_name", "provider"]

    def create(self, validated_data):
        validated_data.pop("provider", None)
        password = validated_data.pop("password")
        user = User.objects.create_user(password=password, **validated_data)
        Profile.objects.get_or_create(user=user, defaults={"provider": "password"})
        return user
