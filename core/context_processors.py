import json

from django.conf import settings
from django.utils.functional import SimpleLazyObject

from . import antispam

from .themes import active_theme


def site_settings(request):
    from .models import SiteConfig
    try:
        config = SiteConfig.load()
    except Exception:
        config = None

    theme = active_theme(request, config)
    theme_ctx = {
        "THEME": theme,
        "THEME_TOKENS": json.dumps({"colors": theme["colors"], "display": theme["font_display"], "body": theme["font_body"]}),
        "THEME_PREVIEW": theme["key"] != (config.theme if config else theme["key"]),
        "THEME_NAVBAR": [f"public/themes/{theme['key']}/navbar.html", "public/includes/navbar.html"],
        "ANTISPAM_TOKEN": SimpleLazyObject(antispam.make_token),
        "THEME_FOOTER": [f"public/themes/{theme['key']}/footer.html", "public/includes/footer.html"],
    }

    if config:
        return {
            **theme_ctx,
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
        **theme_ctx,
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
