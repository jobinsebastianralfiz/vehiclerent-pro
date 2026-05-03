from django.urls import path
from . import views

urlpatterns = [
    # Public
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("terms/", views.terms, name="terms"),
    path("privacy/", views.privacy, name="privacy"),
    path("faq/", views.faq, name="faq"),
    path("contact/", views.contact, name="contact"),
    path("api/chat/", views.chat_search, name="chat_search"),
    path("sitemap.xml", views.sitemap_xml, name="sitemap_xml"),
    path("robots.txt", views.robots_txt, name="robots_txt"),
    # Auth
    path("manage/login/", views.admin_login, name="admin_login"),
    path("manage/logout/", views.admin_logout, name="admin_logout"),
    # Admin: Site Settings
    path("manage/settings/", views.site_config_edit, name="site_config_edit"),
    path("manage/settings/testimonials/", views.testimonial_list, name="testimonial_list"),
    path("manage/settings/testimonials/add/", views.testimonial_add, name="testimonial_add"),
    path("manage/settings/testimonials/<int:pk>/edit/", views.testimonial_edit, name="testimonial_edit"),
    path("manage/settings/testimonials/<int:pk>/delete/", views.testimonial_delete, name="testimonial_delete"),
]
