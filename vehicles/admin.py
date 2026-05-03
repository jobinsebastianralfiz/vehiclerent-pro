from django.contrib import admin

from .models import (
    BookingAddon,
    City,
    Vehicle,
    VehicleCategory,
    VehicleImage,
    WeddingDecorationPackage,
)


class VehicleImageInline(admin.TabularInline):
    model = VehicleImage
    extra = 1


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = (
        "name", "brand", "category", "status", "rental_mode",
        "price_per_day", "is_premium", "is_wedding_service",
        "is_chauffeur_available", "is_published",
    )
    list_filter = (
        "status", "category", "vehicle_type", "fuel_type", "transmission",
        "rental_mode", "is_premium", "is_wedding_service", "is_chauffeur_available",
        "wedding_tier", "is_featured", "is_published",
    )
    search_fields = ("name", "brand", "model", "registration_number", "slug")
    readonly_fields = ("slug", "total_trips", "created_at", "updated_at")
    filter_horizontal = ("available_cities",)
    inlines = [VehicleImageInline]


@admin.register(VehicleCategory)
class VehicleCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "icon", "display_order", "is_active", "vehicle_count")
    list_editable = ("display_order", "is_active")
    search_fields = ("name", "slug")
    readonly_fields = ("slug",)


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("name", "state", "is_hub", "is_active", "display_order")
    list_filter = ("state", "is_hub", "is_active")
    list_editable = ("is_hub", "is_active", "display_order")
    search_fields = ("name", "slug")
    readonly_fields = ("slug",)


@admin.register(BookingAddon)
class BookingAddonAdmin(admin.ModelAdmin):
    list_display = ("name", "icon", "price", "pricing_unit", "display_order", "is_active")
    list_filter = ("pricing_unit", "is_active")
    list_editable = ("price", "is_active", "display_order")
    search_fields = ("name", "slug")
    readonly_fields = ("slug",)


@admin.register(WeddingDecorationPackage)
class WeddingDecorationPackageAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "display_order", "is_active")
    list_filter = ("is_active",)
    list_editable = ("price", "is_active", "display_order")
    search_fields = ("name", "slug")
    readonly_fields = ("slug",)
