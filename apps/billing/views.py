from django.shortcuts import render, get_object_or_404, redirect
from apps.members.models import Member, MembershipHistory, PersonalTrainer
from .models import Payment
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.db import models
from django.db.models import Q, Sum, F, Value, CharField, Case, When, DecimalField
from django.core.paginator import Paginator
from django.contrib import messages
from decimal import Decimal
from datetime import date


@never_cache
@login_required(login_url='login')
def submit_due(request):
    members_with_due = Member.objects.annotate(
        membership_due=Sum(F('membership_history__total_amount') - F('membership_history__paid_amount')),
        pt_due=Sum(F('personal_trainer__total_amount') - F('personal_trainer__paid_amount')),
    ).filter(Q(membership_due__gt=0) | Q(pt_due__gt=0)).distinct()

    selected_member = None
    total_due_amount = 0
    active_plan = None

    member_id = request.GET.get('member_id') or request.POST.get('member_id')

    if member_id:
        selected_member = get_object_or_404(Member, id=member_id)
        
        # Calculate total due amount for the selected member
        membership_due_info = selected_member.membership_history.aggregate(
            total_due=Sum(F('total_amount') - F('paid_amount'))
        )
        membership_due = membership_due_info['total_due'] or 0

        pt_due_info = selected_member.personal_trainer.aggregate(
            total_due=Sum(F('total_amount') - F('paid_amount'))
        )
        pt_due = pt_due_info['total_due'] or 0

        total_due_amount = membership_due + pt_due

        # Get the active plan
        active_plan = selected_member.membership_history.filter(membership_start_date__isnull=False).order_by('-membership_start_date').first()

    if request.method == 'POST' and 'amount_paid' in request.POST:
        amount_paid_str = request.POST.get('amount_paid')
        payment_mode = request.POST.get('payment_mode')
        transaction_id = request.POST.get('transaction_id')
        comment = request.POST.get('comment')

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
            payment = Payment.objects.create(
                member=selected_member,
                amount=amount_paid,
                payment_mode=payment_mode,
                transaction_id=transaction_id,
                comment=comment
            )

            payment_left = amount_paid

            # Pay off membership dues first
            outstanding_memberships = selected_member.membership_history.annotate(
                due=F('total_amount') - F('paid_amount')
            ).filter(due__gt=0).order_by('membership_start_date')

            for history in outstanding_memberships:
                if payment_left == 0:
                    break
                payable_amount = min(history.due, payment_left)
                history.paid_amount += payable_amount
                history.save()
                payment_left -= payable_amount

            # Pay off personal training dues next
            outstanding_pts = selected_member.personal_trainer.annotate(
                due=F('total_amount') - F('paid_amount')
            ).filter(due__gt=0).order_by('pt_start_date')

            for pt in outstanding_pts:
                if payment_left == 0:
                    break
                payable_amount = min(pt.due, payment_left)
                pt.paid_amount += payable_amount
                pt.save()
                payment_left -= payable_amount

            messages.success(request, 'Payment submitted successfully.')
            return redirect('billing:payment_invoice', payment_id=payment.id)

    context = {
        'members': members_with_due,
        'selected_member': selected_member,
        'total_due_amount': total_due_amount,
        'active_plan': active_plan,
    }
    return render(request, 'billing/submit_due.html', context)

@never_cache
@login_required(login_url='login')
def payment_invoice(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    context = {
        'payment': payment,
    }
    return render(request, 'billing/payment_invoice.html', context)





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
def pt_invoice(request, member_id, pt_invoice_id):
    member = get_object_or_404(Member, id=member_id)
    pt_invoice = get_object_or_404(PersonalTrainer, id=pt_invoice_id)

    # Get all PT invoices for the member to find the next and previous
    member_pt_invoices = list(PersonalTrainer.objects.filter(member=member).order_by('created_at'))
    current_invoice_index = member_pt_invoices.index(pt_invoice)

    previous_invoice = member_pt_invoices[current_invoice_index - 1] if current_invoice_index > 0 else None
    next_invoice = member_pt_invoices[current_invoice_index + 1] if current_invoice_index < len(member_pt_invoices) - 1 else None

    context = {
        'member': member,
        'pt_invoice': pt_invoice,
        'previous_invoice': previous_invoice,
        'next_invoice': next_invoice,
    }
    return render(request, 'billing/pt_invoice.html', context)

@never_cache
@login_required(login_url='login')
def invoices_list(request):
    # Get query parameters
    query = request.GET.get('q', '')  # Default to an empty string
    status_filter = request.GET.get('status')
    sort_by = request.GET.get('sort', '-date')

    # Fetch membership invoices
    membership_invoices = MembershipHistory.objects.select_related('member', 'plan').annotate(
        date=F('created_at'),
        type=Value('membership', output_field=models.CharField()),
        amount=F('total_amount'),
        due_amount=F('total_amount') - F('paid_amount'),
        invoice_id=F('id'),
        plan_title=F('plan__title')
    ).values('invoice_id', 'date', 'type', 'amount', 'member_id', 'member__first_name', 'member__last_name', 'plan_title', 'due_amount')

    # Fetch personal training invoices
    pt_invoices = PersonalTrainer.objects.select_related('member', 'trainer').annotate(
        date=F('created_at'),
        type=Value('pt', output_field=models.CharField()),
        amount=F('total_amount'),
        due_amount=F('total_amount') - F('paid_amount'),
        invoice_id=F('id'),
        plan_title=F('trainer__name')
    ).values('invoice_id', 'date', 'type', 'amount', 'member_id', 'member__first_name', 'member__last_name', 'plan_title', 'due_amount')

    # Fetch payment invoices
    payment_invoices = Payment.objects.select_related('member').annotate(
        date=F('payment_date'),
        type=Value('payment', output_field=models.CharField()),
        plan_title=Value('N/A', output_field=models.CharField()),
        due_amount=Value(0, output_field=models.DecimalField()),
        invoice_id=F('id')
    ).values('invoice_id', 'date', 'type', 'amount', 'member_id', 'member__first_name', 'member__last_name', 'plan_title', 'due_amount')

    # Combine and sort invoices
    all_invoices = sorted(
        list(membership_invoices) + list(pt_invoices) + list(payment_invoices),
        key=lambda x: x['date'],
        reverse='-' in sort_by
    )

    # Apply search filter
    if query:
        all_invoices = [inv for inv in all_invoices if 
                        query.lower() in inv['member__first_name'].lower() or 
                        query.lower() in inv['member__last_name'].lower() or 
                        (inv['type'] == 'membership' and query.lower() in inv['plan__title'].lower())]

    # Apply status filter
    if status_filter:
        if status_filter == 'paid':
            all_invoices = [inv for inv in all_invoices if inv['type'] == 'payment' or (inv['type'] == 'membership' and inv['due_amount'] == 0)]
        elif status_filter == 'unpaid':
            all_invoices = [inv for inv in all_invoices if inv['type'] == 'membership' and inv['due_amount'] > 0]

    # Pagination
    paginator = Paginator(all_invoices, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'billing/invoices_list.html', {
        'invoices': page_obj,
        'sort_by': sort_by,
        'status_filter': status_filter,
        'query': query,
    })