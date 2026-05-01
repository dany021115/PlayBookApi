"""Signals for Prediction lifecycle: fan-out push notifications."""

from __future__ import annotations

import logging

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from predictions.models import Prediction

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Prediction)
def _capture_old_state(sender, instance: Prediction, **kwargs):
    if instance.pk:
        try:
            old = sender.objects.only("status").get(pk=instance.pk)
            instance._old_status = old.status
        except sender.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=Prediction)
def _on_prediction_changed(sender, instance: Prediction, created: bool, **kwargs):
    try:
        from notifications.tasks import (
            fan_out_new_prediction,
            fan_out_settled_prediction,
        )
    except Exception:
        return  # notifications app not loaded; nothing to do

    if created:
        try:
            fan_out_new_prediction.delay(instance.id)
        except Exception as exc:
            logger.warning("fan_out_new_prediction enqueue failed: %s", exc)
        return

    old = getattr(instance, "_old_status", None)
    if old != Prediction.Status.SETTLED and instance.status == Prediction.Status.SETTLED:
        try:
            fan_out_settled_prediction.delay(instance.id)
        except Exception as exc:
            logger.warning("fan_out_settled_prediction enqueue failed: %s", exc)
