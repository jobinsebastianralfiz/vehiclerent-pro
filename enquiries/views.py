from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from .forms import EnquiryPublicForm, EnquiryUpdateForm
from .models import Enquiry


# ──────────────── Public Views ────────────────

@require_POST
def submit_enquiry(request):
    form = EnquiryPublicForm(request.POST)
    if form.is_valid():
        form.save()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"success": True})
        messages.success(request, "Thank you! We've received your enquiry and will get back to you shortly.")
        return redirect(request.META.get("HTTP_REFERER", "/"))

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"success": False, "errors": form.errors}, status=400)
    messages.error(request, "Please correct the errors in the form.")
    return redirect(request.META.get("HTTP_REFERER", "/"))


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
