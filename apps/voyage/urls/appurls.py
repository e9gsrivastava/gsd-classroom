from django.urls import path

from ..views.appviews import VoyageDefaultView

urlpatterns = [
    path("", VoyageDefaultView.as_view(), name="home"),
]
