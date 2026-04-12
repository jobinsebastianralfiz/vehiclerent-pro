from django.urls import path
from . import views

urlpatterns = [
    path("manage/allocations/", views.allocation_list, name="allocation_list"),
    path("manage/allocations/add/", views.allocation_add, name="allocation_add"),
    path("manage/allocations/<int:pk>/", views.allocation_detail, name="allocation_detail"),
    path("manage/allocations/<int:pk>/edit/", views.allocation_edit, name="allocation_edit"),
    path("manage/allocations/<int:pk>/complete/", views.allocation_complete, name="allocation_complete"),
    path("manage/allocations/<int:pk>/cancel/", views.allocation_cancel, name="allocation_cancel"),
]
