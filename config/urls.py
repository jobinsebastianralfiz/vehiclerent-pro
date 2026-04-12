from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

urlpatterns = [
    path("", include("core.urls")),
    path("", include("vehicles.urls")),
    path("", include("enquiries.urls")),
    path("", include("dashboard.urls")),
    path("", include("customers.urls")),
    path("", include("allocations.urls")),
]

# Serve media files — in production on Railway, media is on a volume mount
# and Django serves them directly (no separate nginx)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
