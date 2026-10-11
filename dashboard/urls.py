from django.urls import path
from . import views

urlpatterns = [
    path("manage/", views.dashboard, name="dashboard"),
    path("manage/search/", views.admin_search, name="admin_search"),
    path("manage/performance/", views.performance, name="performance"),
    path("manage/performance/speed/", views.performance_speed_save, name="performance_speed_save"),
    path("manage/sitemap/", views.sitemap_admin, name="sitemap_admin"),
]
