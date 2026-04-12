from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Vehicle, VehicleCategory, VehicleImage
from .forms import VehicleForm, CategoryForm, VehicleImageFormSet


# ──────────────── Public Views ────────────────

def vehicle_list(request):
    qs = (
        Vehicle.objects.filter(is_published=True)
        .exclude(status="inactive")
        .select_related("category")
    )

    search = request.GET.get("search", "").strip()
    if search:
        qs = qs.filter(Q(name__icontains=search) | Q(brand__icontains=search) | Q(model__icontains=search))

    vehicle_type = request.GET.get("type")
    if vehicle_type:
        qs = qs.filter(vehicle_type=vehicle_type)

    category_id = request.GET.get("category")
    if category_id:
        qs = qs.filter(category_id=category_id)

    brand = request.GET.get("brand")
    if brand:
        qs = qs.filter(brand__iexact=brand)

    fuel = request.GET.get("fuel")
    if fuel:
        qs = qs.filter(fuel_type=fuel)

    transmission = request.GET.get("transmission")
    if transmission:
        qs = qs.filter(transmission=transmission)

    featured = request.GET.get("featured")
    if featured == "1":
        qs = qs.filter(is_featured=True)

    rental_mode = request.GET.get("rental")
    if rental_mode:
        qs = qs.filter(rental_mode=rental_mode)

    sort = request.GET.get("sort", "-created_at")
    sort_map = {"price": "price_per_day", "-price": "-price_per_day", "name": "name", "-created": "-created_at"}
    qs = qs.order_by(sort_map.get(sort, "-created_at"))

    paginator = Paginator(qs, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    categories = VehicleCategory.objects.filter(is_active=True).order_by("display_order")
    brands = Vehicle.objects.filter(is_published=True).exclude(status="inactive").values_list("brand", flat=True).distinct().order_by("brand")

    query_params = request.GET.copy()
    query_params.pop("page", None)
    query_string = query_params.urlencode()

    return render(request, "public/vehicle_list.html", {
        "page_obj": page_obj,
        "categories": categories,
        "brands": brands,
        "vehicle_types": Vehicle.VEHICLE_TYPE_CHOICES,
        "fuel_types": Vehicle.FUEL_TYPE_CHOICES,
        "transmission_types": Vehicle.TRANSMISSION_CHOICES,
        "rental_modes": Vehicle.RENTAL_MODE_CHOICES,
        "search": search,
        "current_type": vehicle_type,
        "current_category": category_id,
        "current_brand": brand,
        "current_fuel": fuel,
        "current_transmission": transmission,
        "current_rental": rental_mode,
        "current_sort": sort,
        "query_string": query_string,
        "total_count": paginator.count,
    })


def vehicle_detail(request, slug):
    vehicle = get_object_or_404(Vehicle, slug=slug, is_published=True)
    images = vehicle.images.order_by("display_order")
    related = (
        Vehicle.objects.filter(is_published=True, category=vehicle.category)
        .exclude(pk=vehicle.pk, status="inactive")
        .select_related("category")[:4]
    )
    return render(request, "public/vehicle_detail.html", {
        "vehicle": vehicle,
        "images": images,
        "related_vehicles": related,
    })


# ──────────────── Admin Views ────────────────

@login_required
def vehicle_manage_list(request):
    qs = Vehicle.objects.select_related("category").all()
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(brand__icontains=q) | Q(registration_number__icontains=q))
    status = request.GET.get("status")
    if status:
        qs = qs.filter(status=status)

    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "manage/vehicles/list.html", {
        "page_obj": page_obj,
        "q": q,
        "current_status": status,
        "status_choices": Vehicle.STATUS_CHOICES,
    })


def _save_gallery_images(request, vehicle):
    """Save multiple uploaded gallery images to a vehicle."""
    files = request.FILES.getlist("gallery_images")
    start_order = vehicle.images.count()
    for i, f in enumerate(files):
        VehicleImage.objects.create(
            vehicle=vehicle,
            image=f,
            display_order=start_order + i,
        )


@login_required
def vehicle_add(request):
    if request.method == "POST":
        form = VehicleForm(request.POST, request.FILES)
        if form.is_valid():
            vehicle = form.save()
            _save_gallery_images(request, vehicle)
            img_count = request.FILES.getlist("gallery_images")
            messages.success(request, f"Vehicle '{vehicle.name}' created with {len(img_count)} gallery image(s).")
            return redirect("vehicle_manage_list")
    else:
        form = VehicleForm()

    return render(request, "manage/vehicles/form.html", {"form": form, "title": "Add New Vehicle"})


@login_required
def vehicle_edit(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if request.method == "POST":
        form = VehicleForm(request.POST, request.FILES, instance=vehicle)
        if form.is_valid():
            form.save()
            _save_gallery_images(request, vehicle)
            messages.success(request, f"Vehicle '{vehicle.name}' updated successfully.")
            return redirect("vehicle_manage_list")
    else:
        form = VehicleForm(instance=vehicle)

    return render(request, "manage/vehicles/form.html", {"form": form, "title": f"Edit {vehicle.name}", "vehicle": vehicle})


@login_required
def vehicle_delete(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if request.method == "POST":
        try:
            name = vehicle.name
            vehicle.delete()
            messages.success(request, f"Vehicle '{name}' deleted.")
        except Exception:
            messages.error(request, "Cannot delete this vehicle. It has associated allocations.")
        return redirect("vehicle_manage_list")
    return redirect("vehicle_manage_list")


@login_required
def vehicle_images(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if request.method == "POST":
        formset = VehicleImageFormSet(request.POST, request.FILES, instance=vehicle)
        if formset.is_valid():
            formset.save()
            messages.success(request, "Images updated successfully.")
            return redirect("vehicle_images", pk=vehicle.pk)
    else:
        formset = VehicleImageFormSet(instance=vehicle)

    return render(request, "manage/vehicles/images.html", {
        "vehicle": vehicle,
        "formset": formset,
    })


@login_required
def vehicle_toggle_status(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "toggle_featured":
            vehicle.is_featured = not vehicle.is_featured
            vehicle.save(update_fields=["is_featured"])
        elif action == "toggle_published":
            vehicle.is_published = not vehicle.is_published
            vehicle.save(update_fields=["is_published"])
        elif action == "set_status":
            new_status = request.POST.get("status")
            if new_status in dict(Vehicle.STATUS_CHOICES):
                vehicle.status = new_status
                vehicle.save(update_fields=["status"])
        messages.success(request, f"Vehicle '{vehicle.name}' updated.")
    return redirect("vehicle_manage_list")


# ──────────────── Category Admin Views ────────────────

@login_required
def category_list(request):
    categories = VehicleCategory.objects.all().order_by("display_order")
    return render(request, "manage/categories/list.html", {"categories": categories})


@login_required
def category_add(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category created successfully.")
            return redirect("category_list")
    else:
        form = CategoryForm()
    return render(request, "manage/categories/form.html", {"form": form, "title": "Add Category"})


@login_required
def category_edit(request, pk):
    category = get_object_or_404(VehicleCategory, pk=pk)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated successfully.")
            return redirect("category_list")
    else:
        form = CategoryForm(instance=category)
    return render(request, "manage/categories/form.html", {"form": form, "title": f"Edit {category.name}", "category": category})


@login_required
def category_delete(request, pk):
    category = get_object_or_404(VehicleCategory, pk=pk)
    if request.method == "POST":
        category.delete()
        messages.success(request, "Category deleted.")
    return redirect("category_list")
