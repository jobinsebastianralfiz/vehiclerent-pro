from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CustomerForm
from .models import Customer


@login_required
def customer_list(request):
    qs = Customer.objects.all()
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(full_name__icontains=q) | Q(phone__icontains=q) | Q(email__icontains=q))

    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "manage/customers/list.html", {"page_obj": page_obj, "q": q})


@login_required
def customer_add(request):
    if request.method == "POST":
        form = CustomerForm(request.POST, request.FILES)
        if form.is_valid():
            customer = form.save()
            messages.success(request, f"Customer '{customer.full_name}' created.")
            return redirect("customer_list")
    else:
        initial = {}
        # Pre-fill from enquiry if provided
        from enquiries.models import Enquiry
        enquiry_id = request.GET.get("from_enquiry")
        if enquiry_id:
            try:
                enq = Enquiry.objects.get(pk=enquiry_id)
                initial = {"full_name": enq.name, "phone": enq.phone, "email": enq.email}
            except Enquiry.DoesNotExist:
                pass
        form = CustomerForm(initial=initial)
    return render(request, "manage/customers/form.html", {"form": form, "title": "Add Customer"})


@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    allocations = customer.allocations.select_related("vehicle").order_by("-created_at")
    return render(request, "manage/customers/detail.html", {"customer": customer, "allocations": allocations})


@login_required
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == "POST":
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, f"Customer '{customer.full_name}' updated.")
            return redirect("customer_detail", pk=customer.pk)
    else:
        form = CustomerForm(instance=customer)
    return render(request, "manage/customers/form.html", {"form": form, "title": f"Edit {customer.full_name}", "customer": customer})


@login_required
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == "POST":
        try:
            name = customer.full_name
            customer.delete()
            messages.success(request, f"Customer '{name}' deleted.")
        except Exception:
            messages.error(request, "Cannot delete this customer. They have associated allocations.")
        return redirect("customer_list")
    return redirect("customer_list")
