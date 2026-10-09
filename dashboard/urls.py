from django.urls import path
from . import views

urlpatterns = [
    path("manage/", views.dashboard, name="dashboard"),
    path("manage/search/", views.admin_search, name="admin_search"),
]
