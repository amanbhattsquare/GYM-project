from django.shortcuts import render, get_object_or_404, redirect
from apps.members.models import Member, MembershipHistory
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.db.models import Q, F, Sum, Case, When, DecimalField
from django.core.paginator import Paginator
from django.contrib import messages
from decimal import Decimal
from datetime import date


@never_cache
@login_required(login_url='login')
def submit_due(request):
    members_with_due = Member.objects.annotate(
        due_total=Sum(F('membership_history__total_amount') - F('membership_history__paid_amount'))
    ).filter(due_total__gt=0)

    selected_member = None
    total_due_amount = 0
    active_plan = None

    member_id = request.GET.get('member_id') or request.POST.get('member_id')

    if member_id:
        selected_member = get_object_or_404(Member, id=member_id)
        
        # Calculate total due amount for the selected member
        due_info = selected_member.membership_history.aggregate(
            total_due=Sum(F('total_amount') - F('paid_amount'))
        )
        total_due_amount = due_info['total_due'] or 0

        # Get the active plan
        active_plan = selected_member.membership_history.annotate(
            due=F('total_amount') - F('paid_amount')
        ).filter(due__gt=0).order_by('-membership_start_date').first()

    if request.method == 'POST' and 'amount_paid' in request.POST:
        amount_paid_str = request.POST.get('amount_paid')
        payment_mode = request.POST.get('payment_mode')

        try:
            amount_paid = Decimal(amount_paid_str)
        except (ValueError, TypeError):
            messages.error(request, 'Invalid amount paid.')
            return redirect(f"/billing/submit_due/?member_id={member_id}")

        if amount_paid <= 0:
            messages.error(request, 'Amount paid must be a positive number.')
        elif amount_paid > total_due_amount:
            messages.error(request, f'Amount paid cannot be greater than the due amount of {total_due_amount}.')
        else:
            # Apply payment to the oldest outstanding dues first
            outstanding_histories = selected_member.membership_history.annotate(
                due=F('total_amount') - F('paid_amount')
            ).filter(due__gt=0).order_by('membership_start_date')

            payment_left = amount_paid
            last_updated_history = None
            for history in outstanding_histories:
                if payment_left == 0:
                    break
                
                payable_amount = min(history.due, payment_left)
                history.paid_amount += payable_amount
                history.save()
                payment_left -= payable_amount
                last_updated_history = history

            messages.success(request, 'Payment submitted successfully.')
            if last_updated_history:
                return redirect('billing:invoice', member_id=selected_member.id, history_id=last_updated_history.id)
            return redirect(f"/billing/submit_due/?member_id={member_id}")

    context = {
        'members': members_with_due,
        'selected_member': selected_member,
        'total_due_amount': total_due_amount,
        'active_plan': active_plan,
    }
    return render(request, 'billing/submit_due.html', context)





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