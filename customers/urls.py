from django.urls import path
from . import views

urlpatterns = [
    path("manage/customers/", views.customer_list, name="customer_list"),
    path("manage/customers/add/", views.customer_add, name="customer_add"),
    path("manage/customers/<int:pk>/", views.customer_detail, name="customer_detail"),
    path("manage/customers/<int:pk>/edit/", views.customer_edit, name="customer_edit"),
    path("manage/customers/<int:pk>/delete/", views.customer_delete, name="customer_delete"),
]
