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
