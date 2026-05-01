from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_api_key.permissions import HasAPIKey

from markets.api.v1.serializers import (
    BookmakerSerializer,
    EventDetailSerializer,
    EventListSerializer,
    OddsSnapshotSerializer,
    SportSerializer,
)
from markets.models import Bookmaker, Event, OddsSnapshot, Sport


CACHE_TTL_LIVE = 15
CACHE_TTL_PREMATCH = 60
CACHE_TTL_SCHEDULE = 6 * 60 * 60


class SportListView(generics.ListAPIView):
    serializer_class = SportSerializer
    queryset = Sport.objects.all()
    pagination_class = None
    permission_classes = [IsAuthenticated, HasAPIKey]

    @method_decorator(cache_page(CACHE_TTL_SCHEDULE))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class BookmakerListView(generics.ListAPIView):
    serializer_class = BookmakerSerializer
    queryset = Bookmaker.objects.all()
    pagination_class = None
    permission_classes = [IsAuthenticated, HasAPIKey]


class _BaseEventQuery:
    def get_base_queryset(self):
        return (
            Event.objects.select_related("league__sport", "home_team", "away_team")
        )


class MatchListView(_BaseEventQuery, generics.ListAPIView):
    serializer_class = EventListSerializer
    permission_classes = [IsAuthenticated, HasAPIKey]
    filterset_fields = ["status", "league__sport__key", "league__slug"]

    def get_queryset(self):
        qs = self.get_base_queryset()
        sport = self.request.query_params.get("sport")
        if sport:
            qs = qs.filter(league__sport__key__iexact=sport)
        status = self.request.query_params.get("status")
        if status:
            qs = qs.filter(status=status)
        return qs

    @method_decorator(cache_page(CACHE_TTL_PREMATCH))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class LiveMatchListView(_BaseEventQuery, generics.ListAPIView):
    serializer_class = EventListSerializer
    pagination_class = None
    permission_classes = [IsAuthenticated, HasAPIKey]

    def get_queryset(self):
        qs = self.get_base_queryset().filter(status=Event.Status.LIVE)
        sport = self.request.query_params.get("sport")
        if sport:
            qs = qs.filter(league__sport__key__iexact=sport)
        return qs

    @method_decorator(cache_page(CACHE_TTL_LIVE))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class MatchDetailView(_BaseEventQuery, generics.RetrieveAPIView):
    serializer_class = EventDetailSerializer
    permission_classes = [IsAuthenticated, HasAPIKey]

    def get_queryset(self):
        return self.get_base_queryset()


def _latest_per_outcome(qs):
    seen: set[tuple] = set()
    out = []
    for snap in qs.order_by("-captured_at"):
        key = (snap.event_id, snap.bookmaker_id, snap.market, snap.outcome)
        if key in seen:
            continue
        seen.add(key)
        out.append(snap)
    return out


class OddsBySportView(generics.ListAPIView):
    serializer_class = OddsSnapshotSerializer
    permission_classes = [IsAuthenticated, HasAPIKey]
    queryset = OddsSnapshot.objects.none()

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return OddsSnapshot.objects.none()
        sport = self.kwargs["sport"].lower()
        qs = OddsSnapshot.objects.select_related(
            "event__league__sport", "event__home_team", "event__away_team", "bookmaker",
        ).filter(event__league__sport__key__iexact=sport)
        market = self.request.query_params.get("market")
        if market:
            qs = qs.filter(market=market)
        bookmaker = self.request.query_params.get("bookmaker")
        if bookmaker:
            qs = qs.filter(bookmaker__slug=bookmaker)
        return qs

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        latest = _latest_per_outcome(qs)
        page = self.paginate_queryset(latest)
        ser = self.get_serializer(page if page is not None else latest, many=True)
        if page is not None:
            return self.get_paginated_response(ser.data)
        return Response(ser.data)

    @method_decorator(cache_page(CACHE_TTL_PREMATCH))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class OddsByEventView(generics.ListAPIView):
    serializer_class = OddsSnapshotSerializer
    pagination_class = None
    permission_classes = [IsAuthenticated, HasAPIKey]
    queryset = OddsSnapshot.objects.none()

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return OddsSnapshot.objects.none()
        event_id = self.kwargs["event_id"]
        get_object_or_404(Event, pk=event_id)
        return OddsSnapshot.objects.select_related(
            "event__league__sport", "event__home_team", "event__away_team", "bookmaker",
        ).filter(event_id=event_id)

    def list(self, request, *args, **kwargs):
        latest = _latest_per_outcome(self.get_queryset())
        return Response(self.get_serializer(latest, many=True).data)

    @method_decorator(cache_page(CACHE_TTL_LIVE))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
