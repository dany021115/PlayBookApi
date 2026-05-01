from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_api_key.permissions import HasAPIKey

from follows.api.v1.serializers import (
    FollowedLeagueSerializer,
    FollowedSportSerializer,
    FollowedStrategySerializer,
    SavedPredictionSerializer,
)
from follows.models import (
    FollowedLeague,
    FollowedSport,
    FollowedStrategy,
    SavedPrediction,
)


class _OwnedListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, HasAPIKey]
    pagination_class = None

    def get_queryset(self):
        return self.queryset_cls.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class _OwnedDestroyView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, HasAPIKey]

    def get_queryset(self):
        return self.queryset_cls.objects.filter(user=self.request.user)


class FollowedSportListCreate(_OwnedListCreateView):
    serializer_class = FollowedSportSerializer
    queryset_cls = FollowedSport


class FollowedSportDestroy(_OwnedDestroyView):
    serializer_class = FollowedSportSerializer
    queryset_cls = FollowedSport


class FollowedLeagueListCreate(_OwnedListCreateView):
    serializer_class = FollowedLeagueSerializer
    queryset_cls = FollowedLeague


class FollowedLeagueDestroy(_OwnedDestroyView):
    serializer_class = FollowedLeagueSerializer
    queryset_cls = FollowedLeague


class FollowedStrategyListCreate(_OwnedListCreateView):
    serializer_class = FollowedStrategySerializer
    queryset_cls = FollowedStrategy


class FollowedStrategyDestroy(_OwnedDestroyView):
    serializer_class = FollowedStrategySerializer
    queryset_cls = FollowedStrategy


class SavedPredictionListCreate(_OwnedListCreateView):
    serializer_class = SavedPredictionSerializer
    queryset_cls = SavedPrediction


class SavedPredictionDestroy(_OwnedDestroyView):
    serializer_class = SavedPredictionSerializer
    queryset_cls = SavedPrediction
