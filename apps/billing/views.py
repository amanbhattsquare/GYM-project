from django.shortcuts import render, get_object_or_404
from apps.members.models import Member, MembershipHistory
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.db.models import Q
from django.core.paginator import Paginator

# Create your views here.

@never_cache
@login_required(login_url='login')
def invoice(request, member_id, history_id):
    member = get_object_or_404(Member, id=member_id)
    history = get_object_or_404(MembershipHistory, id=history_id)

    # Get all invoices for the member to find the next and previous
    member_invoices = list(MembershipHistory.objects.filter(member=member).order_by('created_at'))
    current_invoice_index = member_invoices.index(history)

    previous_invoice = member_invoices[current_invoice_index - 1] if current_invoice_index > 0 else None
    next_invoice = member_invoices[current_invoice_index + 1] if current_invoice_index < len(member_invoices) - 1 else None

    context = {
        'member': member,
        'history': history,
        'previous_invoice': previous_invoice,
        'next_invoice': next_invoice,
    }
    return render(request, 'billing/invoice.html', context)

@never_cache
@login_required(login_url='login')
def invoices_list(request):
    invoices = MembershipHistory.objects.select_related('member', 'plan').all()

    # Search
    query = request.GET.get('q')
    if query:
        invoices = invoices.filter(
            Q(member__first_name__icontains=query) |
            Q(member__last_name__icontains=query) |
            Q(plan__title__icontains=query)
        ).distinct()

    # Filtering
    status_filter = request.GET.get('status')
    if status_filter == 'paid':
        invoices = invoices.filter(due_amount=0)
    elif status_filter == 'unpaid':
        invoices = invoices.filter(due_amount__gt=0)
    elif status_filter == 'overdue':
        invoices = invoices.filter(due_amount__gt=0, plan__end_date__lt=date.today())

    # Sorting
    sort_by = request.GET.get('sort', '-created_at')
    invoices = invoices.order_by(sort_by)

    # Pagination
    paginator = Paginator(invoices, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'billing/invoices_list.html', {
        'invoices': page_obj,
        'sort_by': sort_by,
        'status_filter': status_filter,
        'query': query,
    })

@never_cache
@login_required(login_url='login')
def payments_list(request):
    payments = MembershipHistory.objects.select_related('member', 'plan').all()

    # Search
    query = request.GET.get('q')
    if query:
        payments = payments.filter(
            Q(member__first_name__icontains=query) |
            Q(member__last_name__icontains=query) |
            Q(plan__title__icontains=query)
        ).distinct()

    # Filtering
    payment_mode_filter = request.GET.get('payment_mode')
    if payment_mode_filter:
        payments = payments.filter(payment_mode=payment_mode_filter)

    # Sorting
    sort_by = request.GET.get('sort', '-created_at')
    payments = payments.order_by(sort_by)

    # Pagination
    paginator = Paginator(payments, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'billing/payments_list.html', {
        'payments': page_obj,
        'sort_by': sort_by,
        'payment_mode_filter': payment_mode_filter,
        'query': query,
    })