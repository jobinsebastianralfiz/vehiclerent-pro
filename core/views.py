from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import models
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render

from vehicles.models import Vehicle, VehicleCategory

from .forms import AdminLoginForm, SiteConfigForm, TestimonialForm
from .models import SiteConfig, Testimonial


# ──────────────── Public Views ────────────────

def home(request):
    config = SiteConfig.load()
    categories = (
        VehicleCategory.objects.filter(is_active=True)
        .annotate(count=Count("vehicles", filter=models.Q(vehicles__is_published=True, vehicles__status__in=["available", "rented", "reserved"])))
        .order_by("display_order")
    )
    featured_vehicles = (
        Vehicle.objects.filter(is_featured=True, is_published=True)
        .exclude(status="inactive")
        .select_related("category")[:8]
    )
    testimonials = Testimonial.objects.filter(is_active=True)[:6]
    # Collect hero background images
    hero_bg_images = []
    if config:
        for field in [config.hero_bg_1, config.hero_bg_2, config.hero_bg_3]:
            if field:
                hero_bg_images.append(field.url)
    return render(request, "public/home.html", {
        "config": config,
        "categories": categories,
        "featured_vehicles": featured_vehicles,
        "testimonials": testimonials,
        "hero_bg_images": hero_bg_images,
    })


def about(request):
    config = SiteConfig.load()
    testimonials = Testimonial.objects.filter(is_active=True)[:6]
    return render(request, "public/about.html", {
        "config": config,
        "testimonials": testimonials,
    })


def terms(request):
    return render(request, "public/terms.html")


def privacy(request):
    return render(request, "public/privacy.html")


def faq(request):
    faq_items = [
        {"q": "What documents do I need to rent a vehicle?", "a": "You'll need a valid driving license, a government-issued photo ID (Aadhaar, Passport, or Voter ID), and a recent address proof. All documents must be original and valid at the time of rental pickup."},
        {"q": "How do I book a vehicle?", "a": 'Browse our <a href="/vehicles/" class="text-primary font-medium hover:underline">fleet page</a>, select a vehicle you like, and either send us an enquiry through the form or message us directly on WhatsApp. Our team will confirm availability and finalize the booking.'},
        {"q": "What are the rental rates?", "a": "Rates vary by vehicle type. Each vehicle listing shows the daily rate, and many include weekly and monthly rates at a discount. Security deposits may apply for premium vehicles. All prices are clearly displayed on the vehicle detail page."},
        {"q": "Is there a minimum rental period?", "a": "The minimum rental period is 1 day (24 hours). We also offer weekly and monthly plans at discounted rates for longer rentals."},
        {"q": "What is the cancellation policy?", "a": "Cancellations made more than 48 hours before pickup receive a full refund. 24-48 hours before pickup: 50% refund. Less than 24 hours: no refund. Please refer to our <a href='/terms/' class='text-primary font-medium hover:underline'>Terms of Service</a> for full details."},
        {"q": "Is fuel included in the rental price?", "a": "No, fuel is not included. Vehicles are provided with a certain fuel level and should be returned at the same level. Tolls and parking charges are also the renter's responsibility."},
        {"q": "What happens if the vehicle breaks down?", "a": "In case of a breakdown, contact us immediately. We will arrange for roadside assistance or a replacement vehicle as quickly as possible, at no extra cost if the breakdown is not due to renter negligence."},
        {"q": "Can I extend my rental period?", "a": "Yes, extensions are subject to vehicle availability. Please contact us at least 24 hours before your scheduled return to request an extension. Extended days will be charged at the applicable daily rate."},
        {"q": "Is insurance included?", "a": "Basic third-party liability insurance is included as required by law. Comprehensive coverage may be available as an add-on. You are responsible for any damage deductibles not covered by insurance."},
        {"q": "Do you offer self-drive and chauffeur-driven options?", "a": "We primarily offer self-drive rentals. For chauffeur-driven options, please contact us directly and we'll do our best to accommodate your request."},
        {"q": "What is the security deposit?", "a": "A refundable security deposit may be required depending on the vehicle. The amount is listed on each vehicle's page. The deposit is returned upon satisfactory vehicle return, minus any deductions for damage or fines."},
        {"q": "What are the age requirements?", "a": "Renters must be at least 21 years of age and hold a valid driving license that has been active for at least 1 year."},
    ]
    return render(request, "public/faq.html", {"faq_items": faq_items})


def contact(request):
    config = SiteConfig.load()
    return render(request, "public/contact.html", {"config": config})


# ──────────────── Auth Views ────────────────

def admin_login(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = AdminLoginForm()
    error = None
    if request.method == "POST":
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            user = authenticate(request, username=form.cleaned_data["email"], password=form.cleaned_data["password"])
            if user is not None:
                login(request, user)
                return redirect(request.GET.get("next", "/manage/"))
            else:
                error = "Invalid email or password."
    return render(request, "manage/login.html", {"form": form, "error": error})


def admin_logout(request):
    logout(request)
    return redirect("admin_login")


# ──────────────── Admin: Site Settings ────────────────

@login_required
def site_config_edit(request):
    config = SiteConfig.load()
    if request.method == "POST":
        form = SiteConfigForm(request.POST, request.FILES, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, "Site settings updated successfully.")
            return redirect("site_config_edit")
    else:
        form = SiteConfigForm(instance=config)
    return render(request, "manage/settings/config.html", {"form": form, "config": config})


# ──────────────── Admin: Testimonials ────────────────

@login_required
def testimonial_list(request):
    testimonials = Testimonial.objects.all()
    return render(request, "manage/settings/testimonials.html", {"testimonials": testimonials})


@login_required
def testimonial_add(request):
    if request.method == "POST":
        form = TestimonialForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Testimonial added.")
            return redirect("testimonial_list")
    else:
        form = TestimonialForm()
    return render(request, "manage/settings/testimonial_form.html", {"form": form, "title": "Add Testimonial"})


@login_required
def testimonial_edit(request, pk):
    testimonial = get_object_or_404(Testimonial, pk=pk)
    if request.method == "POST":
        form = TestimonialForm(request.POST, request.FILES, instance=testimonial)
        if form.is_valid():
            form.save()
            messages.success(request, "Testimonial updated.")
            return redirect("testimonial_list")
    else:
        form = TestimonialForm(instance=testimonial)
    return render(request, "manage/settings/testimonial_form.html", {"form": form, "title": f"Edit Testimonial", "testimonial": testimonial})


@login_required
def testimonial_delete(request, pk):
    testimonial = get_object_or_404(Testimonial, pk=pk)
    if request.method == "POST":
        testimonial.delete()
        messages.success(request, "Testimonial deleted.")
    return redirect("testimonial_list")
