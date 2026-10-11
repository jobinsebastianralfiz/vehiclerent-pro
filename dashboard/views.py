from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncDate
from django.shortcuts import render
from django.utils import timezone

from allocations.models import Allocation
from customers.models import Customer
from enquiries.models import Enquiry
from vehicles.models import City, Vehicle

SPARK_DAYS = 14


def _daily(qs, field="created_at"):
    """Counts per day for the last SPARK_DAYS days (oldest first), for the stat sparklines."""
    today = timezone.localdate()
    start = today - timedelta(days=SPARK_DAYS - 1)
    rows = (
        qs.filter(**{f"{field}__date__gte": start})
        .annotate(d=TruncDate(field))
        .values("d")
        .annotate(n=Count("id"))
    )
    by_day = {r["d"]: r["n"] for r in rows}
    return [by_day.get(start + timedelta(days=i), 0) for i in range(SPARK_DAYS)]


@login_required
def dashboard(request):
    now = timezone.localtime()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    today = now.date()

    total_vehicles = Vehicle.objects.count()
    available = Vehicle.objects.filter(status="available").count()
    rented = Vehicle.objects.filter(status="rented").count()
    stats = {
        "total_vehicles": total_vehicles,
        "available_vehicles": available,
        "rented_vehicles": rented,
        "available_pct": round(available * 100 / total_vehicles) if total_vehicles else 0,
        "rented_pct": round(rented * 100 / total_vehicles) if total_vehicles else 0,
        "vehicles_this_month": Vehicle.objects.filter(created_at__gte=month_start).count(),
        "premium_vehicles": Vehicle.objects.filter(is_premium=True, is_published=True).count(),
        "wedding_vehicles": Vehicle.objects.filter(is_wedding_service=True, is_published=True).count(),
        "total_cities": City.objects.filter(is_active=True).count(),
        "total_customers": Customer.objects.count(),
        "customers_this_month": Customer.objects.filter(created_at__gte=month_start).count(),
        "active_allocations": Allocation.objects.filter(status="active").count(),
        "allocations_this_month": Allocation.objects.filter(created_at__gte=month_start).count(),
        "new_enquiries": Enquiry.objects.filter(status="new").count(),
        "enquiries_today": Enquiry.objects.filter(created_at__date=today).count(),
    }
    spark = {
        "vehicles": _daily(Vehicle.objects.all()),
        "customers": _daily(Customer.objects.all()),
        "allocations": _daily(Allocation.objects.all()),
        "enquiries": _daily(Enquiry.objects.all()),
    }
    earning = Allocation.objects.filter(status__in=["active", "completed"])
    revenue = {
        "month": earning.filter(start_date__gte=month_start.date()).aggregate(t=Sum("total_amount"))["t"] or 0,
        "all": earning.aggregate(t=Sum("total_amount"))["t"] or 0,
    }

    recent_enquiries = Enquiry.objects.select_related("vehicle").order_by("-created_at")[:5]
    recent_allocations = Allocation.objects.select_related("vehicle", "customer").order_by("-created_at")[:5]

    return render(request, "manage/dashboard.html", {
        "stats": stats,
        "spark": spark,
        "revenue": revenue,
        "today": today,
        "recent_enquiries": recent_enquiries,
        "recent_allocations": recent_allocations,
    })


@login_required
def admin_search(request):
    """One search box for the admin top bar: vehicles, customers and enquiries."""
    q = (request.GET.get("q") or "").strip()[:100]
    results = {"vehicles": [], "customers": [], "enquiries": []}
    if q:
        results["vehicles"] = Vehicle.objects.filter(
            Q(name__icontains=q) | Q(brand__icontains=q) | Q(registration_number__icontains=q)
        ).order_by("brand", "name")[:20]
        results["customers"] = Customer.objects.filter(
            Q(full_name__icontains=q) | Q(phone__icontains=q) | Q(email__icontains=q)
        )[:20]
        results["enquiries"] = Enquiry.objects.select_related("vehicle").filter(
            Q(name__icontains=q) | Q(phone__icontains=q) | Q(email__icontains=q) | Q(message__icontains=q)
        ).order_by("-created_at")[:20]
    total = sum(len(v) for v in results.values())
    return render(request, "manage/search.html", {"search_q": q, "results": results, "total": total})


# ──────────────── Performance (visitor analytics + page speed) ────────────────

PERIODS = [(7, "7 days"), (30, "30 days"), (90, "90 days")]


def _speed_pages():
    """(label, path) of the pages worth speed-testing: the main pages plus the three most-viewed cars."""
    from django.urls import reverse
    from core.models import PageView
    pages = [("Home", reverse("home")), ("Fleet", reverse("vehicle_list")), ("Wedding cars", reverse("wedding_cars")),
             ("Contact", reverse("contact"))]
    top = (PageView.objects.exclude(vehicle_slug="").values("vehicle_slug").annotate(n=Count("id")).order_by("-n")[:3])
    names = {v.slug: v for v in Vehicle.objects.filter(slug__in=[t["vehicle_slug"] for t in top])}
    for t in top:
        v = names.get(t["vehicle_slug"])
        if v:
            pages.append((v.full_name, v.get_absolute_url()))
    if len(pages) == 4:
        v = Vehicle.objects.filter(is_published=True).order_by("-is_featured", "name").first()
        if v:
            pages.append((v.full_name, v.get_absolute_url()))
    return pages


@login_required
def performance(request):
    from django.conf import settings
    from core.models import PageView, SpeedResult
    try:
        days = int(request.GET.get("days", 30))
    except ValueError:
        days = 30
    days = days if days in dict(PERIODS) else 30
    today = timezone.localdate()
    start = today - timedelta(days=days - 1)
    views = PageView.objects.filter(created_at__date__gte=start)
    prev = PageView.objects.filter(created_at__date__gte=start - timedelta(days=days), created_at__date__lt=start)
    enquiries = Enquiry.objects.filter(created_at__date__gte=start)

    total = views.count()
    visitors = views.values("visitor", "created_at__date").distinct().count()
    prev_total = prev.count()
    n_enq = enquiries.count()

    per_day = {r["d"]: r["n"] for r in views.annotate(d=TruncDate("created_at")).values("d").annotate(n=Count("id"))}
    daily = [(start + timedelta(days=i), per_day.get(start + timedelta(days=i), 0)) for i in range(days)]
    peak = max([n for _, n in daily] + [1])

    labels = dict(PageView.SOURCE_CHOICES)
    sources = [{"key": r["source"], "label": labels.get(r["source"], r["source"]), "n": r["n"]}
               for r in views.values("source").annotate(n=Count("id")).order_by("-n")]
    devices = [{"label": dict(PageView.DEVICE_CHOICES).get(r["device"], r["device"]), "n": r["n"]}
               for r in views.values("device").annotate(n=Count("id")).order_by("-n")]
    pages = list(views.values("path").annotate(n=Count("id"), u=Count("visitor", distinct=True)).order_by("-n")[:12])
    ai_hosts = list(views.filter(source="ai").values("referrer_host").annotate(n=Count("id")).order_by("-n")[:6])

    car_views = {r["vehicle_slug"]: r["n"] for r in views.exclude(vehicle_slug="").values("vehicle_slug").annotate(n=Count("id"))}
    car_enq = {r["vehicle_id"]: r["n"] for r in enquiries.exclude(vehicle=None).values("vehicle_id").annotate(n=Count("id"))}
    cars = sorted(({"v": v, "views": car_views.get(v.slug, 0), "enquiries": car_enq.get(v.id, 0)}
                   for v in Vehicle.objects.filter(is_published=True)), key=lambda c: (-c["views"], -c["enquiries"]))[:10]

    speed = {(r.path, r.strategy): r for r in SpeedResult.objects.all()}
    speed_rows = [{"label": label, "path": path, "mobile": speed.get((path, "mobile")), "desktop": speed.get((path, "desktop"))}
                  for label, path in _speed_pages()]

    return render(request, "manage/performance.html", {
        "days": days, "periods": PERIODS, "start": start, "today": today,
        "total": total, "visitors": visitors, "n_enq": n_enq,
        "change": round((total - prev_total) * 100 / prev_total) if prev_total >= 20 else None,  # tiny bases give silly percentages
        "conversion": round(n_enq * 100 / visitors, 1) if visitors else 0,
        "ai_views": sum(s["n"] for s in sources if s["key"] == "ai"),
        "daily": daily, "peak": peak, "sources": sources, "devices": devices, "pages": pages, "cars": cars,
        "ai_hosts": ai_hosts, "speed_rows": speed_rows, "pagespeed_key": settings.PAGESPEED_API_KEY,
        "site_url": f"{request.scheme}://{request.get_host()}",
    })


@login_required
def performance_speed_save(request):
    """Stores a PageSpeed result the admin page fetched in the browser (POST: path, strategy, score, lcp_ms, cls, tbt_ms)."""
    from django.http import JsonResponse
    from core.models import SpeedResult
    if request.method != "POST":
        return JsonResponse({"ok": False}, status=405)
    p = request.POST
    if p.get("strategy") not in ("mobile", "desktop") or not p.get("path", "").startswith("/"):
        return JsonResponse({"ok": False}, status=400)
    def num(key, cast=int):
        try:
            return cast(float(p.get(key)))
        except (TypeError, ValueError):
            return None
    score = num("score")
    if score is None or not 0 <= score <= 100:
        return JsonResponse({"ok": False}, status=400)
    SpeedResult.objects.update_or_create(path=p["path"][:300], strategy=p["strategy"],
                                         defaults={"score": score, "lcp_ms": num("lcp_ms"), "cls": num("cls", float), "tbt_ms": num("tbt_ms")})
    return JsonResponse({"ok": True})


@login_required
def sitemap_admin(request):
    from core.views import sitemap_entries
    entries = sitemap_entries()
    return render(request, "manage/sitemap.html", {
        "entries": entries, "site_url": f"{request.scheme}://{request.get_host()}",
        "n_pages": sum(1 for e in entries if e["kind"] == "Page"), "n_cars": sum(1 for e in entries if e["kind"] == "Vehicle"),
    })
