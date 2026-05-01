"""Reusable DRF view + serializer mixins (TeeShot-style)."""

from rest_framework import serializers


class UserFilterAPIMixin:
    """Filter list view's queryset to records owned by request.user."""

    user_field = "user"
    include_null_values = False

    def get_queryset(self):
        qs = super().get_queryset()
        kwargs = {self.user_field: self.request.user}
        if self.include_null_values:
            return qs.filter(**kwargs) | qs.filter(**{f"{self.user_field}__isnull": True})
        return qs.filter(**kwargs)


class UserOwnershipValidatorMixin:
    """Serializer mixin: validate that an FK target belongs to request.user."""

    def validate_user_ownership(self, obj, user_field: str = "user"):
        request = self.context.get("request")
        if obj is None or request is None or not request.user.is_authenticated:
            return
        owner = getattr(obj, user_field, None)
        if owner != request.user:
            raise serializers.ValidationError("Object does not belong to current user.")
