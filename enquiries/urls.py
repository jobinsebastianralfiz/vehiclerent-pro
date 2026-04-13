from django.urls import path
from . import views

urlpatterns = [
    # Public
    path("enquiry/submit/", views.submit_enquiry, name="submit_enquiry"),
    # Admin
    path("manage/enquiries/", views.enquiry_list, name="enquiry_list"),
    path("manage/enquiries/<int:pk>/", views.enquiry_detail, name="enquiry_detail"),
    path("manage/enquiries/<int:pk>/delete/", views.enquiry_delete, name="enquiry_delete"),
    path("manage/api/enquiry-check/", views.enquiry_check_new, name="enquiry_check_new"),
]
