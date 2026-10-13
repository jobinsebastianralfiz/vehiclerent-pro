from django.urls import path

from . import views

urlpatterns = [
    path("tours/", views.tour_list, name="tour_list"),
    path("tours/<slug:slug>/", views.tour_detail, name="tour_detail"),
    path("manage/tours/", views.tour_manage_list, name="tour_manage_list"),
    path("manage/tours/add/", views.tour_add, name="tour_add"),
    path("manage/tours/<int:pk>/edit/", views.tour_edit, name="tour_edit"),
    path("manage/tours/<int:pk>/delete/", views.tour_delete, name="tour_delete"),
]
