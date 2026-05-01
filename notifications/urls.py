from django.urls import path

from notifications.api.v1.endpoints.views import DeviceRegisterView

app_name = "notifications"

urlpatterns = [
    path("devices/register/", DeviceRegisterView.as_view(), name="device-register"),
]
