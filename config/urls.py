import posixpath

from django.conf import settings
from django.http import Http404
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

# Always serve media files (Railway/Namecheap have no separate media server).
# Customer ID proofs and licences are admin-only; everything else is public.
def media(request, path):
    clean = posixpath.normpath(path).lstrip("/")
    if clean.split("/", 1)[0] == "customers" and not request.user.is_authenticated:
        raise Http404
    return serve(request, clean, document_root=settings.MEDIA_ROOT)


urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', media),
]
