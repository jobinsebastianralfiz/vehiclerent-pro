from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from core.models import SiteConfig
from core.themes import themed

from .forms import TourPackageForm
from .models import TourPackage


def _places(text):
    return [p.strip() for p in (text or "").split(",") if p.strip()]


def tour_context(config=None):
    """Published packages split by scope, plus the destination chips for the "nothing here yet" cards.
    Shared by the home page section and the Tours page."""
    config = config or SiteConfig.load()
    packages = list(TourPackage.objects.filter(is_published=True))
    return {
        "tours_dom": [t for t in packages if t.scope == "domestic"],
        "tours_intl": [t for t in packages if t.scope == "international"],
        "tour_places_dom": _places(getattr(config, "tours_domestic_places", "")),
        "tour_places_intl": _places(getattr(config, "tours_international_places", "")),
    }


def tour_list(request):
    scope = request.GET.get("scope")
    ctx = tour_context()
    if scope not in ("domestic", "international"):
        scope = "international" if not ctx["tours_dom"] and ctx["tours_intl"] else "domestic"
    return render(request, themed(request, "tour_list.html"), {**ctx, "scope": scope})


def tour_detail(request, slug):
    tour = get_object_or_404(TourPackage, slug=slug, is_published=True)
    more = TourPackage.objects.filter(is_published=True, scope=tour.scope).exclude(pk=tour.pk)[:3]
    return render(request, themed(request, "tour_detail.html"), {"tour": tour, "more_tours": more})


# ──────────────── Admin ────────────────

@login_required
def tour_manage_list(request):
    scope = request.GET.get("scope", "")
    tours = TourPackage.objects.all()
    if scope in ("domestic", "international"):
        tours = tours.filter(scope=scope)
    return render(request, "manage/tours/list.html", {"tours": tours, "scope": scope,
                                                      "counts": {s: TourPackage.objects.filter(scope=s).count() for s in ("domestic", "international")}})


def _save(request, tour=None):
    form = TourPackageForm(request.POST or None, request.FILES or None, instance=tour)
    if request.method == "POST" and form.is_valid():
        saved = form.save()
        messages.success(request, f"“{saved.title}” saved." + ("" if saved.is_published else " It's hidden until you tick Published."))
        return redirect("tour_manage_list")
    return render(request, "manage/tours/form.html", {"form": form, "tour": tour,
                                                      "title": f"Edit {tour.title}" if tour else "Add Tour Package"})


@login_required
def tour_add(request):
    return _save(request)


@login_required
def tour_edit(request, pk):
    return _save(request, get_object_or_404(TourPackage, pk=pk))


@login_required
def tour_delete(request, pk):
    tour = get_object_or_404(TourPackage, pk=pk)
    if request.method == "POST":
        tour.delete()
        messages.success(request, "Tour package deleted.")
    return redirect("tour_manage_list")
