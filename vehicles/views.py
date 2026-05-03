from django.core.paginator import Paginator
from django.db import models
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import (
    BookingAddon,
    City,
    Vehicle,
    VehicleCategory,
    VehicleImage,
    WeddingDecorationPackage,
)
from .forms import (
    BookingAddonForm,
    CategoryForm,
    CityForm,
    VehicleForm,
    VehicleImageFormSet,
    WeddingDecorationPackageForm,
)


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

    premium = request.GET.get("premium")
    if premium == "1":
        qs = qs.filter(is_premium=True)

    wedding = request.GET.get("wedding")
    if wedding == "1":
        qs = qs.filter(is_wedding_service=True)

    rental_mode = request.GET.get("rental")
    if rental_mode:
        qs = qs.filter(rental_mode=rental_mode)

    rental_type = request.GET.get("rental_type")  # "self_drive" or "with_driver"
    if rental_type == "with_driver":
        qs = qs.filter(is_chauffeur_available=True)

    pickup_city = request.GET.get("pickup_city")
    if pickup_city:
        # Match vehicles explicitly tagged with this city, OR vehicles with no
        # cities set at all (treated as "available everywhere").
        qs = qs.filter(
            Q(available_cities__slug=pickup_city) | Q(available_cities__isnull=True)
        ).distinct()

    sort = request.GET.get("sort", "-created_at")
    sort_map = {"price": "price_per_day", "-price": "-price_per_day", "name": "name", "-created": "-created_at"}
    qs = qs.order_by(sort_map.get(sort, "-created_at"))

    paginator = Paginator(qs, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    categories = VehicleCategory.objects.filter(is_active=True).order_by("display_order")
    brands = Vehicle.objects.filter(is_published=True).exclude(status="inactive").values_list("brand", flat=True).distinct().order_by("brand")
    cities = City.objects.filter(is_active=True)

    query_params = request.GET.copy()
    query_params.pop("page", None)
    query_string = query_params.urlencode()

    return render(request, "public/vehicle_list.html", {
        "page_obj": page_obj,
        "categories": categories,
        "brands": brands,
        "cities": cities,
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
        "current_rental_type": rental_type,
        "current_pickup_city": pickup_city,
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
    addons = BookingAddon.objects.filter(is_active=True)
    cities = City.objects.filter(is_active=True)
    return render(request, "public/vehicle_detail.html", {
        "vehicle": vehicle,
        "images": images,
        "related_vehicles": related,
        "addons": addons,
        "cities": cities,
    })


def premium_cars(request):
    """Premium / luxury fleet landing page."""
    qs = (
        Vehicle.objects.filter(is_published=True, is_premium=True)
        .exclude(status="inactive")
        .select_related("category")
        .order_by("-is_featured", "-price_per_day")
    )
    cities = City.objects.filter(is_active=True)
    return render(request, "public/premium_cars.html", {
        "vehicles": qs,
        "featured_vehicles": qs.filter(is_featured=True)[:3],
        "cities": cities,
    })


def wedding_cars(request):
    """Wedding Cars landing page with tier-segmented showcase."""
    qs = (
        Vehicle.objects.filter(is_published=True, is_wedding_service=True)
        .exclude(status="inactive")
        .select_related("category")
    )
    classic = qs.filter(wedding_tier="classic")[:6]
    premium = qs.filter(wedding_tier="premium")[:6]
    iconic = qs.filter(wedding_tier="iconic")[:6]
    other = qs.exclude(wedding_tier__in=["classic", "premium", "iconic"])[:6]
    decorations = WeddingDecorationPackage.objects.filter(is_active=True)
    cities = City.objects.filter(is_active=True)
    return render(request, "public/wedding_cars.html", {
        "vehicles": qs,
        "classic_cars": classic,
        "premium_cars": premium,
        "iconic_cars": iconic,
        "other_cars": other,
        "decorations": decorations,
        "cities": cities,
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
    categories = (
        VehicleCategory.objects.all()
        .annotate(vehicle_count=Count("vehicles", filter=models.Q(vehicles__is_published=True)))
        .order_by("display_order")
    )
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


# ──────────────── City Admin Views ────────────────

@login_required
def city_list(request):
    cities = City.objects.all()
    return render(request, "manage/cities/list.html", {"cities": cities})


@login_required
def city_add(request):
    form = CityForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "City added.")
        return redirect("city_list")
    return render(request, "manage/cities/form.html", {"form": form, "title": "Add City"})


@login_required
def city_edit(request, pk):
    city = get_object_or_404(City, pk=pk)
    form = CityForm(request.POST or None, instance=city)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "City updated.")
        return redirect("city_list")
    return render(request, "manage/cities/form.html", {"form": form, "title": f"Edit {city.name}", "city": city})


@login_required
def city_delete(request, pk):
    city = get_object_or_404(City, pk=pk)
    if request.method == "POST":
        city.delete()
        messages.success(request, "City deleted.")
    return redirect("city_list")


# ──────────────── Booking Addon Admin Views ────────────────

@login_required
def addon_list(request):
    addons = BookingAddon.objects.all()
    return render(request, "manage/addons/list.html", {"addons": addons})


@login_required
def addon_add(request):
    form = BookingAddonForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Add-on added.")
        return redirect("addon_list")
    return render(request, "manage/addons/form.html", {"form": form, "title": "Add Booking Add-on"})


@login_required
def addon_edit(request, pk):
    addon = get_object_or_404(BookingAddon, pk=pk)
    form = BookingAddonForm(request.POST or None, instance=addon)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Add-on updated.")
        return redirect("addon_list")
    return render(request, "manage/addons/form.html", {"form": form, "title": f"Edit {addon.name}", "addon": addon})


@login_required
def addon_delete(request, pk):
    addon = get_object_or_404(BookingAddon, pk=pk)
    if request.method == "POST":
        addon.delete()
        messages.success(request, "Add-on deleted.")
    return redirect("addon_list")


# ──────────────── Wedding Decoration Package Admin ────────────────

@login_required
def decoration_list(request):
    decorations = WeddingDecorationPackage.objects.all()
    return render(request, "manage/decorations/list.html", {"decorations": decorations})


@login_required
def decoration_add(request):
    form = WeddingDecorationPackageForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Decoration package added.")
        return redirect("decoration_list")
    return render(request, "manage/decorations/form.html", {"form": form, "title": "Add Decoration Package"})


@login_required
def decoration_edit(request, pk):
    decoration = get_object_or_404(WeddingDecorationPackage, pk=pk)
    form = WeddingDecorationPackageForm(request.POST or None, request.FILES or None, instance=decoration)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Decoration package updated.")
        return redirect("decoration_list")
    return render(request, "manage/decorations/form.html", {"form": form, "title": f"Edit {decoration.name}", "decoration": decoration})


@login_required
def decoration_delete(request, pk):
    decoration = get_object_or_404(WeddingDecorationPackage, pk=pk)
    if request.method == "POST":
        decoration.delete()
        messages.success(request, "Decoration package deleted.")
    return redirect("decoration_list")
