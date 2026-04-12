from django.conf import settings


def site_settings(request):
    from .models import SiteConfig
    try:
        config = SiteConfig.load()
    except Exception:
        config = None

    if config:
        return {
            "SITE_CONFIG": config,
            "BUSINESS_NAME": config.site_name,
            "BUSINESS_PHONE": config.phone,
            "BUSINESS_EMAIL": config.email,
            "BUSINESS_ADDRESS": config.address,
            "WHATSAPP_NUMBER": config.whatsapp_number,
            "WHATSAPP_DEFAULT_MESSAGE": config.whatsapp_default_message,
        }

    # Fallback to env vars
    return {
        "SITE_CONFIG": None,
        "BUSINESS_NAME": settings.BUSINESS_NAME,
        "BUSINESS_PHONE": settings.BUSINESS_PHONE,
        "BUSINESS_EMAIL": settings.BUSINESS_EMAIL,
        "BUSINESS_ADDRESS": settings.BUSINESS_ADDRESS,
        "WHATSAPP_NUMBER": settings.WHATSAPP_NUMBER,
        "WHATSAPP_DEFAULT_MESSAGE": settings.WHATSAPP_DEFAULT_MESSAGE,
    }


def whatsapp_config(request):
    # Now handled by site_settings, keep for backward compat
    return {}


def admin_context(request):
    if request.path.startswith("/manage/") and request.user.is_authenticated:
        from enquiries.models import Enquiry
        return {"new_enquiry_count": Enquiry.objects.filter(status="new").count()}
    return {}
