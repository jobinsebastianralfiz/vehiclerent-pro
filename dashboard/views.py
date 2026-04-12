from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render

from allocations.models import Allocation
from customers.models import Customer
from enquiries.models import Enquiry
from vehicles.models import Vehicle


@login_required
def dashboard(request):
    stats = {
        "total_vehicles": Vehicle.objects.count(),
        "available_vehicles": Vehicle.objects.filter(status="available").count(),
        "rented_vehicles": Vehicle.objects.filter(status="rented").count(),
        "total_customers": Customer.objects.count(),
        "active_allocations": Allocation.objects.filter(status="active").count(),
        "new_enquiries": Enquiry.objects.filter(status="new").count(),
    }
    total_revenue = (
        Allocation.objects.filter(status__in=["active", "completed"])
        .aggregate(total=Sum("total_amount"))["total"]
    ) or 0

    recent_enquiries = (
        Enquiry.objects.select_related("vehicle")
        .order_by("-created_at")[:5]
    )
    recent_allocations = (
        Allocation.objects.select_related("vehicle", "customer")
        .order_by("-created_at")[:5]
    )

    return render(request, "manage/dashboard.html", {
        "stats": stats,
        "total_revenue": total_revenue,
        "recent_enquiries": recent_enquiries,
        "recent_allocations": recent_allocations,
    })
