from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.http import Http404
from django_ratelimit.decorators import ratelimit

from .forms import EnquiryPublicForm, EnquiryUpdateForm
from .models import Enquiry
from core import antispam
from core.themes import themed

# Enquiry ids this browser submitted; the thank-you page only shows these.
SESSION_ENQUIRIES = "my_enquiries"


# ──────────────── Public Views ────────────────

@require_POST
@ratelimit(key=antispam.client_ip, rate="5/10m", block=False)
@ratelimit(key=antispam.client_ip, rate="20/d", block=False)
def submit_enquiry(request):
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    if getattr(request, "limited", False):
        msg = "Too many enquiries from your connection. Please call or WhatsApp us instead."
        if is_ajax:
            return JsonResponse({"success": False, "errors": {"__all__": [msg]}}, status=429)
        messages.error(request, msg)
        return redirect("contact")
    spam = antispam.check(request)
    if spam == "token":
        msg = "This page was open too long. Please refresh and send again."
        if is_ajax:
            return JsonResponse({"success": False, "errors": {"__all__": [msg]}}, status=400)
        messages.error(request, msg)
        return redirect("contact")
    if spam:
        # Look like success so bots don't learn what tripped them; nothing is saved.
        if is_ajax:
            return JsonResponse({"success": True, "enquiry_id": None, "whatsapp_message": "", "whatsapp_url": "", "thanks_url": "/"})
        return redirect("home")
    form = EnquiryPublicForm(request.POST)
    if form.is_valid():
        enquiry = form.save()
        mine = request.session.get(SESSION_ENQUIRIES, [])[-19:]
        request.session[SESSION_ENQUIRIES] = mine + [enquiry.id]
        if is_ajax:
            return JsonResponse({
                "success": True,
                "enquiry_id": enquiry.id,
                "whatsapp_message": enquiry.whatsapp_message(),
                "whatsapp_url": _build_whatsapp_url(enquiry),
                "thanks_url": f"/enquiry/thanks/{enquiry.id}/",
            })
        messages.success(request, "Thank you! We've received your enquiry.")
        return redirect("enquiry_thanks", pk=enquiry.id)

    if is_ajax:
        return JsonResponse({"success": False, "errors": form.errors}, status=400)
    messages.error(request, "Please correct the errors in the form.")
    return redirect("contact")


def _build_whatsapp_url(enquiry):
    """Compose a wa.me link with the enquiry details pre-filled."""
    from urllib.parse import quote
    from django.conf import settings as dj_settings
    wa_number = dj_settings.WHATSAPP_NUMBER
    try:
        from core.models import SiteConfig
        config = SiteConfig.load()
        if config and config.whatsapp_number:
            wa_number = config.whatsapp_number
    except Exception:
        pass
    if not wa_number:
        return ""
    return f"https://wa.me/{wa_number}?text={quote(enquiry.whatsapp_message())}"


def enquiry_thanks(request, pk):
    """Public thank-you page after enquiry submission. Auto-opens WhatsApp with booking details.

    Only the browser that sent the enquiry may see it: ids are sequential and the
    page shows the customer's name and phone.
    """
    if pk not in request.session.get(SESSION_ENQUIRIES, []) and not request.user.is_authenticated:
        raise Http404
    enquiry = get_object_or_404(Enquiry, pk=pk)
    return render(request, themed(request, "enquiry_thanks.html"), {
        "enquiry": enquiry,
        "wa_url": _build_whatsapp_url(enquiry),
        "wa_message": enquiry.whatsapp_message(),
    })


# ──────────────── Admin Views ────────────────

@login_required
def enquiry_list(request):
    qs = Enquiry.objects.select_related("vehicle").all()
    status = request.GET.get("status")
    if status:
        qs = qs.filter(status=status)
    source = request.GET.get("source")
    if source:
        qs = qs.filter(source=source)

    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "manage/enquiries/list.html", {
        "page_obj": page_obj,
        "current_status": status,
        "current_source": source,
        "status_choices": Enquiry.STATUS_CHOICES,
        "source_choices": Enquiry.SOURCE_CHOICES,
    })


@login_required
def enquiry_detail(request, pk):
    enquiry = get_object_or_404(Enquiry.objects.select_related("vehicle"), pk=pk)
    if request.method == "POST":
        form = EnquiryUpdateForm(request.POST, instance=enquiry)
        if form.is_valid():
            form.save()
            messages.success(request, "Enquiry updated.")
            return redirect("enquiry_detail", pk=enquiry.pk)
    else:
        form = EnquiryUpdateForm(instance=enquiry)
    return render(request, "manage/enquiries/detail.html", {"enquiry": enquiry, "form": form})


@login_required
def enquiry_delete(request, pk):
    enquiry = get_object_or_404(Enquiry, pk=pk)
    if request.method == "POST":
        enquiry.delete()
        messages.success(request, "Enquiry deleted.")
        return redirect("enquiry_list")
    return redirect("enquiry_list")


@login_required
def enquiry_check_new(request):
    """API endpoint polled by admin to detect new enquiries."""
    count = Enquiry.objects.filter(status="new").count()
    latest = Enquiry.objects.order_by("-id").values_list("id", flat=True).first() or 0
    return JsonResponse({"new_count": count, "latest_id": latest})
