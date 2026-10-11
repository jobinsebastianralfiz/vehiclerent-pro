"""Six-step add/edit vehicle wizard.

Every step is a small ModelForm over one slice of Vehicle fields. Step 1 creates
the vehicle as a draft (is_draft=True, never published); each later step saves
straight to that record, so leaving half way never loses finished steps.
"""
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.urls import reverse

from django.utils import timezone

from . import catalog
from .forms import VehicleForm
from .models import City, Vehicle, VehicleCategory, VehicleImage

STEPS = [
    {"n": 1, "key": "basic", "title": "Basic Info", "sub": "Vehicle details", "icon": "badge",
     "heading": "Basic Information", "lede": "Essential vehicle details and identification",
     "fields": ["name", "brand", "model", "year", "registration_number", "color"]},
    {"n": 2, "key": "class", "title": "Classification", "sub": "Type & category", "icon": "category",
     "heading": "Vehicle Classification", "lede": "Select the vehicle type and category",
     "fields": ["vehicle_type", "category", "seating_capacity", "luggage_capacity", "has_ac"]},
    {"n": 3, "key": "specs", "title": "Specifications", "sub": "Technical & EV", "icon": "tune",
     "heading": "Technical Specifications", "lede": "Engine, fuel and EV details",
     "fields": ["fuel_type", "transmission", "engine_cc", "mileage_kmpl", "battery_capacity_kwh",
                "range_km", "motor_power_kw", "charging_time_hours", "fast_charging"]},
    {"n": 4, "key": "pricing", "title": "Pricing", "sub": "Rates & rental", "icon": "payments",
     "heading": "Rates & Pricing", "lede": "Rental mode and rates. Fill in at least one price.",
     "fields": ["rental_mode", "minimum_rental_days", "price_per_day", "price_per_week", "price_per_month",
                "security_deposit", "with_driver_price_per_day", "per_km_charge", "included_km_per_day",
                "wedding_decoration_charge"]},
    {"n": 5, "key": "content", "title": "Content", "sub": "Description & features", "icon": "description",
     "heading": "Content & Features", "lede": "Descriptions, photo and key highlights",
     "fields": ["short_description", "thumbnail", "description", "features"]},
    {"n": 6, "key": "media", "title": "Media & Settings", "sub": "Images, status & SEO", "icon": "photo_library",
     "heading": "Media & Settings", "lede": "Gallery, visibility, badges and search details",
     "fields": ["status", "is_featured", "show_in_hero", "is_premium", "is_wedding_service", "is_chauffeur_available",
                "wedding_tier", "available_cities", "meta_title", "meta_description", "meta_keywords"]},
]
LAST = len(STEPS)
# Edited from the Quick settings bar on every step once a vehicle is live, so step 6 leaves them out then
QUICK_FIELDS = ["status", "is_featured", "show_in_hero", "is_premium", "is_wedding_service",
                "is_chauffeur_available", "wedding_tier"]

_INPUT = "w-full rounded-xl border-stone-200 text-sm py-2.5 px-3.5 focus:border-[#145c38] focus:ring-[#145c38]/20"
_CHECK = "w-5 h-5 rounded-md border-stone-300 text-[#145c38] focus:ring-[#145c38]/30"


class _StepBase(VehicleForm):
    """Shared widget styling; validation (features JSON) comes from VehicleForm."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            w = field.widget
            if isinstance(w, forms.CheckboxInput):
                w.attrs["class"] = _CHECK
                continue
            if isinstance(w, (forms.CheckboxInput, forms.CheckboxSelectMultiple, forms.HiddenInput, forms.ClearableFileInput)):
                continue
            w.attrs["class"] = _INPUT
        if "category" in self.fields:
            self.fields["category"].queryset = VehicleCategory.objects.filter(is_active=True)
            self.fields["category"].empty_label = "Choose a category"
        if "available_cities" in self.fields:
            self.fields["available_cities"].widget = forms.CheckboxSelectMultiple()
            self.fields["available_cities"].queryset = City.objects.filter(is_active=True)
        if "year" in self.fields:
            this_year = timezone.localdate().year
            years = list(range(this_year + 1, 1949, -1))
            current = self.initial.get("year") or (self.instance.year if self.instance else None)
            if current and current not in years:
                years.append(current)
            self.fields["year"].widget = forms.Select(
                choices=[("", "Choose year")] + [(y, y) for y in years], attrs={"class": _INPUT})
        if "vehicle_type" in self.fields:
            self.fields["vehicle_type"].widget = forms.RadioSelect(choices=Vehicle.VEHICLE_TYPE_CHOICES)
        placeholders = {
            "name": "e.g. Swift Dzire VXi", "brand": "e.g. Maruti Suzuki", "model": "e.g. Dzire",
            "year": "e.g. 2022", "registration_number": "e.g. KL 07 AB 1234", "color": "e.g. White",
            "seating_capacity": "e.g. 5", "luggage_capacity": "e.g. 3", "engine_cc": "e.g. 1197", "mileage_kmpl": "e.g. 21",
            "battery_capacity_kwh": "e.g. 40", "range_km": "e.g. 350", "motor_power_kw": "e.g. 100",
            "charging_time_hours": "e.g. 6", "price_per_day": "e.g. 2500", "price_per_week": "e.g. 15000",
            "price_per_month": "e.g. 50000", "security_deposit": "e.g. 10000", "with_driver_price_per_day": "e.g. 800",
            "per_km_charge": "e.g. 15", "wedding_decoration_charge": "e.g. 3000",
            "short_description": "One or two lines shown on the fleet card",
            "description": "Full description for the vehicle page",
            "meta_title": "e.g. Swift Dzire for Rent in Kochi",
            "meta_keywords": "e.g. swift dzire rent, car rental kochi",
        }
        labels = {
            "engine_cc": "Engine", "mileage_kmpl": "Mileage", "battery_capacity_kwh": "Battery capacity",
            "range_km": "Range", "motor_power_kw": "Motor power", "charging_time_hours": "Charging time",
            "with_driver_price_per_day": "With-driver price per day", "per_km_charge": "Extra km charge",
            "included_km_per_day": "Free km per day", "meta_title": "Meta title", "meta_description": "Meta description",
            "meta_keywords": "Meta keywords", "registration_number": "Registration number",
        }
        for name, text in labels.items():
            if name in self.fields:
                self.fields[name].label = text
        for name in ("fuel_type", "transmission", "wedding_tier"):
            if name in self.fields:
                f = self.fields[name]
                f.choices = [("", "Choose…")] + [c for c in f.choices if c[0] != ""]
        for name, text in placeholders.items():
            if name in self.fields:
                self.fields[name].widget.attrs.setdefault("placeholder", text)
        if "short_description" in self.fields:
            self.fields["short_description"].widget.attrs.update({"rows": 3, "maxlength": 300})
        if "description" in self.fields:
            self.fields["description"].widget.attrs["rows"] = 7
        if "meta_description" in self.fields:
            self.fields["meta_description"].widget = forms.Textarea(attrs={"rows": 3, "maxlength": 300, "class": _INPUT})


def _step_form(step, vehicle=None):
    fields = STEPS[step - 1]["fields"]
    if vehicle is not None and not vehicle.is_draft:
        fields = [f for f in fields if f not in QUICK_FIELDS]
    return forms.modelform_factory(Vehicle, form=_StepBase, fields=fields)


class _PublishForm(forms.Form):
    publish = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={"class": _CHECK}))


def _clean_step(raw):
    try:
        return min(max(int(raw), 1), LAST)
    except (TypeError, ValueError):
        return 1


@login_required
def vehicle_add(request):
    """Step 1 for a new vehicle. Saving it creates the draft; later steps live at vehicle_wizard."""
    return _wizard(request, None, 1)


@login_required
def vehicle_edit(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    step = vehicle.wizard_step if vehicle.is_draft else 1
    return redirect("vehicle_wizard", pk=vehicle.pk, step=step)


@login_required
def vehicle_wizard(request, pk, step):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    step = _clean_step(step)
    if vehicle.is_draft and step > vehicle.wizard_step:
        return redirect("vehicle_wizard", pk=pk, step=vehicle.wizard_step)
    return _wizard(request, vehicle, step)


def _wizard(request, vehicle, step):
    Form = _step_form(step, vehicle)
    is_new = vehicle is None
    live = bool(vehicle and not vehicle.is_draft)
    publish_form = None
    if request.method == "POST":
        form = Form(request.POST, request.FILES, instance=vehicle)
        if step == LAST and not live:
            publish_form = _PublishForm(request.POST)
            publish_form.is_valid()
        action = request.POST.get("action", "next")
        if form.is_valid():
            obj = form.save(commit=False)
            if is_new:
                obj.is_draft = True
                obj.wizard_step = 1
            if step == LAST:
                for img_id in request.POST.getlist("delete_image"):
                    VehicleImage.objects.filter(pk=img_id, vehicle=obj).delete()
            finishing = step == LAST and action == "finish"
            if finishing and not live:
                obj.is_draft = False
                obj.is_published = publish_form.cleaned_data.get("publish", False)
            if obj.is_draft:
                obj.wizard_step = max(obj.wizard_step, min(step + 1, LAST) if action in ("next", "finish") else step)
            obj.save()
            form.save_m2m()
            if step == LAST:
                start = obj.images.count()
                for i, f in enumerate(request.FILES.getlist("gallery_images")):
                    VehicleImage.objects.create(vehicle=obj, image=f, display_order=start + i)

            if finishing:
                messages.success(request, f"Vehicle '{obj.name}' saved{' and published' if obj.is_published else ' (not published)'}.")
                return redirect("vehicle_manage_list")
            if action == "draft":
                messages.success(request, f"Draft saved. You can continue '{obj.name}' from Vehicles any time.")
                return redirect("vehicle_manage_list")
            if action == "prev":
                return redirect("vehicle_wizard", pk=obj.pk, step=max(step - 1, 1))
            if action.startswith("goto:"):
                target = _clean_step(action[5:])
                if obj.is_draft:
                    target = min(target, obj.wizard_step)
                return redirect("vehicle_wizard", pk=obj.pk, step=target)
            if action == "stay":
                messages.success(request, "Saved.")
                return redirect("vehicle_wizard", pk=obj.pk, step=step)
            return redirect("vehicle_wizard", pk=obj.pk, step=min(step + 1, LAST))
        messages.error(request, "Please fix the highlighted fields. Nothing on this step was saved yet.")
    else:
        form = Form(instance=vehicle)
        if step == LAST and not live:
            publish_form = _PublishForm(initial={"publish": True if (vehicle and vehicle.is_draft) else bool(vehicle and vehicle.is_published)})

    reached = LAST if (vehicle and not vehicle.is_draft) else (vehicle.wizard_step if vehicle else 1)
    steps = [dict(s, done=(s["n"] < reached or (vehicle and not vehicle.is_draft)) and s["n"] != step, reachable=s["n"] <= reached) for s in STEPS]
    return render(request, "manage/vehicles/wizard.html", {
        "form": form,
        "publish_form": publish_form,
        "vehicle": vehicle,
        "step": step,
        "steps": steps,
        "current": STEPS[step - 1],
        "last": LAST,
        "is_edit": live,
        "quick": _quick_json(vehicle) if live else None,
        "status_choices": Vehicle.STATUS_CHOICES,
        "tier_choices": [c for c in Vehicle._meta.get_field("wedding_tier").choices if c[0]],
        "draft_key": f"vw-{vehicle.pk if vehicle else 'new'}-{step}",
        "post_url": reverse("vehicle_wizard", args=[vehicle.pk, step]) if vehicle else reverse("vehicle_add"),
        "images": _gallery_json(vehicle) if (vehicle and step == LAST) else [],
        "catalog": catalog.as_json() if step == 1 else None,
        "colors": catalog.COLORS if step == 1 else None,
        "input_class": _INPUT,
    })


GALLERY_MAX_BYTES = 10 * 1024 * 1024


def _gallery_json(vehicle):
    return [{"id": i.pk, "url": i.image.url} for i in vehicle.images.order_by("display_order", "pk")]


def _sync_primary(vehicle):
    """The first gallery photo is the primary one."""
    first = vehicle.images.order_by("display_order", "pk").first()
    vehicle.images.exclude(pk=first.pk if first else None).filter(is_primary=True).update(is_primary=False)
    if first and not first.is_primary:
        VehicleImage.objects.filter(pk=first.pk).update(is_primary=True)


@login_required
@require_POST
def vehicle_gallery(request, pk):
    """Step 6 gallery, saved instantly: op=upload (file), op=delete (id) or op=reorder (ids, in order)."""
    vehicle = get_object_or_404(Vehicle, pk=pk)
    op = request.POST.get("op")
    if op == "upload":
        f = request.FILES.get("file")
        if not f:
            return JsonResponse({"error": "No file received."}, status=400)
        if f.size > GALLERY_MAX_BYTES:
            return JsonResponse({"error": f"{f.name} is over 10 MB."}, status=400)
        try:
            f = forms.ImageField().clean(f)
        except forms.ValidationError:
            return JsonResponse({"error": f"{f.name} isn't a photo we can read."}, status=400)
        last = vehicle.images.order_by("-display_order").first()
        VehicleImage.objects.create(vehicle=vehicle, image=f, display_order=(last.display_order + 1) if last else 0)
    elif op == "delete":
        img = vehicle.images.filter(pk=request.POST.get("id")).first()
        if img:
            img.image.delete(save=False)
            img.delete()
    elif op == "reorder":
        ids = [int(x) for x in request.POST.getlist("ids") if x.isdigit()]
        for n, img_id in enumerate(ids):
            vehicle.images.filter(pk=img_id).update(display_order=n)
    else:
        return JsonResponse({"error": "Unknown action."}, status=400)
    _sync_primary(vehicle)
    return JsonResponse({"images": _gallery_json(vehicle)})


QUICK_FLAGS = ["is_published", "is_featured", "show_in_hero", "is_premium", "is_wedding_service", "is_chauffeur_available"]


def _quick_json(vehicle):
    data = {f: getattr(vehicle, f) for f in QUICK_FLAGS}
    data.update(status=vehicle.status, wedding_tier=vehicle.wedding_tier or "")
    return data


@login_required
@require_POST
def vehicle_quick(request, pk):
    """Quick settings bar: saves one setting of a live vehicle at once (field + value)."""
    vehicle = get_object_or_404(Vehicle, pk=pk, is_draft=False)
    field, value = request.POST.get("field"), request.POST.get("value", "")
    if field in QUICK_FLAGS:
        setattr(vehicle, field, value in ("1", "true", "on"))
    elif field == "status" and value in dict(Vehicle.STATUS_CHOICES):
        vehicle.status = value
    elif field == "wedding_tier" and (value == "" or value in dict(Vehicle._meta.get_field("wedding_tier").choices)):
        vehicle.wedding_tier = value
    else:
        return JsonResponse({"error": "That setting can't be changed here."}, status=400)
    vehicle.save(update_fields=[field])
    return JsonResponse({"quick": _quick_json(vehicle)})
