from django.urls import path

from collector.views import collect_request

urlpatterns = [
    path("requests/", collect_request, name="collect-request"),
]
