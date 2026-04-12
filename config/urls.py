from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path, re_path
from django.views.static import serve

urlpatterns = [
    path("", include("core.urls")),
    path("", include("vehicles.urls")),
    path("", include("enquiries.urls")),
    path("", include("dashboard.urls")),
    path("", include("customers.urls")),
    path("", include("allocations.urls")),
]

# Always serve media files (Railway has no nginx — Django serves directly)
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
