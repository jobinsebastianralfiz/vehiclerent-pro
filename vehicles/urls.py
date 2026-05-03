from django.urls import path
from . import views

urlpatterns = [
    # Public
    path("vehicles/", views.vehicle_list, name="vehicle_list"),
    path("wedding-cars/", views.wedding_cars, name="wedding_cars"),
    path("vehicles/<slug:slug>/", views.vehicle_detail, name="vehicle_detail"),
    # Admin - Vehicles
    path("manage/vehicles/", views.vehicle_manage_list, name="vehicle_manage_list"),
    path("manage/vehicles/add/", views.vehicle_add, name="vehicle_add"),
    path("manage/vehicles/<int:pk>/edit/", views.vehicle_edit, name="vehicle_edit"),
    path("manage/vehicles/<int:pk>/delete/", views.vehicle_delete, name="vehicle_delete"),
    path("manage/vehicles/<int:pk>/images/", views.vehicle_images, name="vehicle_images"),
    path("manage/vehicles/<int:pk>/toggle-status/", views.vehicle_toggle_status, name="vehicle_toggle_status"),
    # Admin - Categories
    path("manage/categories/", views.category_list, name="category_list"),
    path("manage/categories/add/", views.category_add, name="category_add"),
    path("manage/categories/<int:pk>/edit/", views.category_edit, name="category_edit"),
    path("manage/categories/<int:pk>/delete/", views.category_delete, name="category_delete"),
    # Admin - Cities
    path("manage/cities/", views.city_list, name="city_list"),
    path("manage/cities/add/", views.city_add, name="city_add"),
    path("manage/cities/<int:pk>/edit/", views.city_edit, name="city_edit"),
    path("manage/cities/<int:pk>/delete/", views.city_delete, name="city_delete"),
    # Admin - Booking Addons
    path("manage/addons/", views.addon_list, name="addon_list"),
    path("manage/addons/add/", views.addon_add, name="addon_add"),
    path("manage/addons/<int:pk>/edit/", views.addon_edit, name="addon_edit"),
    path("manage/addons/<int:pk>/delete/", views.addon_delete, name="addon_delete"),
    # Admin - Wedding Decoration Packages
    path("manage/decorations/", views.decoration_list, name="decoration_list"),
    path("manage/decorations/add/", views.decoration_add, name="decoration_add"),
    path("manage/decorations/<int:pk>/edit/", views.decoration_edit, name="decoration_edit"),
    path("manage/decorations/<int:pk>/delete/", views.decoration_delete, name="decoration_delete"),
]
