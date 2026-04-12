from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AllocationForm, AllocationCompleteForm
from .models import Allocation
from vehicles.models import Vehicle


@login_required
def allocation_list(request):
    qs = Allocation.objects.select_related("vehicle", "customer").all()
    status = request.GET.get("status")
    if status:
        qs = qs.filter(status=status)

    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "manage/allocations/list.html", {
        "page_obj": page_obj,
        "current_status": status,
        "status_choices": Allocation.STATUS_CHOICES,
    })


@login_required
def allocation_add(request):
    if request.method == "POST":
        form = AllocationForm(request.POST)
        if form.is_valid():
            allocation = form.save()
            messages.success(request, "Allocation created successfully.")
            return redirect("allocation_detail", pk=allocation.pk)
    else:
        form = AllocationForm()

    # Provide vehicle prices as JSON for Alpine.js auto-fill
    vehicle_prices = {
        str(v.pk): str(v.daily_rate_for_allocation)
        for v in Vehicle.objects.filter(status__in=["available", "reserved"])
    }

    return render(request, "manage/allocations/form.html", {
        "form": form,
        "title": "New Allocation",
        "vehicle_prices": vehicle_prices,
    })


@login_required
def allocation_detail(request, pk):
    allocation = get_object_or_404(Allocation.objects.select_related("vehicle", "customer"), pk=pk)
    complete_form = AllocationCompleteForm()
    return render(request, "manage/allocations/detail.html", {
        "allocation": allocation,
        "complete_form": complete_form,
    })


@login_required
def allocation_edit(request, pk):
    allocation = get_object_or_404(Allocation, pk=pk)
    if request.method == "POST":
        form = AllocationForm(request.POST, instance=allocation)
        if form.is_valid():
            form.save()
            messages.success(request, "Allocation updated.")
            return redirect("allocation_detail", pk=allocation.pk)
    else:
        form = AllocationForm(instance=allocation)

    vehicle_prices = {
        str(v.pk): str(v.daily_rate_for_allocation)
        for v in Vehicle.objects.filter(status__in=["available", "reserved", "rented"])
    }

    return render(request, "manage/allocations/form.html", {
        "form": form,
        "title": f"Edit Allocation #{allocation.pk}",
        "allocation": allocation,
        "vehicle_prices": vehicle_prices,
    })


@login_required
def allocation_complete(request, pk):
    allocation = get_object_or_404(Allocation, pk=pk)
    if request.method == "POST":
        form = AllocationCompleteForm(request.POST)
        if form.is_valid():
            allocation.complete(
                actual_return_date=form.cleaned_data["actual_return_date"],
                odometer_end=form.cleaned_data.get("odometer_end"),
            )
            messages.success(request, "Allocation marked as completed.")
    return redirect("allocation_detail", pk=allocation.pk)


@login_required
def allocation_cancel(request, pk):
    allocation = get_object_or_404(Allocation, pk=pk)
    if request.method == "POST":
        allocation.cancel()
        messages.success(request, "Allocation cancelled.")
    return redirect("allocation_detail", pk=allocation.pk)
