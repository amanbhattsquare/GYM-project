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
from django.http import JsonResponse
from django.urls import reverse


@never_cache
@login_required(login_url='login')
def submit_due(request):
    gym = getattr(request, 'gym', None)
    latest_follow_up = Payment.objects.filter(
        member=models.OuterRef('pk'),
        gym=gym
    ).order_by('-follow_up_date').values('follow_up_date')[:1]

    members_with_due = Member.objects.filter(gym=gym).annotate(
        membership_due=Sum(
            F('membership_history__total_amount') - F('membership_history__paid_amount'),
            filter=Q(membership_history__status='active', membership_history__gym=gym)
        ),
        pt_due=Sum(
            F('personal_trainer__total_amount') - F('personal_trainer__paid_amount'),
            filter=Q(personal_trainer__status='active', personal_trainer__gym=gym)
        ),
        latest_follow_up_date=models.Subquery(latest_follow_up)
    ).filter(Q(membership_due__gt=0) | Q(pt_due__gt=0)).distinct()

    query = request.GET.get('q')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    follow_up_date_filter = request.GET.get('follow_up_date')

    if query:
        members_with_due = members_with_due.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(mobile_number__icontains=query) |
            Q(member_id__icontains=query)
        )

    if from_date and to_date:
        members_with_due = members_with_due.filter(latest_follow_up_date__range=[from_date, to_date])
    
    if follow_up_date_filter:
        members_with_due = members_with_due.filter(latest_follow_up_date=follow_up_date_filter)

    paginator = Paginator(members_with_due, 10)  # Show 10 members per page
    page_number = request.GET.get('page')
    members_page = paginator.get_page(page_number)

    if request.method == 'POST' and 'amount_paid' in request.POST:
        member_id = request.POST.get('member_id')
        selected_member = get_object_or_404(Member, id=member_id, gym=gym)

        # Calculate total due amount for the selected member
        membership_due_info = selected_member.membership_history.filter(status='active', gym=gym).aggregate(
            total_due=Sum(F('total_amount') - F('paid_amount'))
        )
        membership_due = membership_due_info['total_due'] or 0

        pt_due_info = selected_member.personal_trainer.filter(status='active', gym=gym).aggregate(
            total_due=Sum(F('total_amount') - F('paid_amount'))
        )
        pt_due = pt_due_info['total_due'] or 0

        total_due_amount = membership_due + pt_due

        amount_paid_str = request.POST.get('amount_paid')
        payment_mode = request.POST.get('payment_mode')
        transaction_id = request.POST.get('transaction_id')
        comment = request.POST.get('comment')
        follow_up_date_str = request.POST.get('follow_up_date')
        follow_up_date = date.fromisoformat(follow_up_date_str) if follow_up_date_str and follow_up_date_str.strip() else None


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
                comment=comment,
                follow_up_date=follow_up_date,
                gym=gym
            )

            payment_left = amount_paid

            # Pay off membership dues first
            outstanding_memberships = selected_member.membership_history.annotate(
                due=F('total_amount') - F('paid_amount')
            ).filter(due__gt=0, gym=gym).order_by('membership_start_date')

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
            ).filter(due__gt=0, gym=gym).order_by('pt_start_date')

            for pt in outstanding_pts:
                if payment_left == 0:
                    break
                payable_amount = min(pt.due, payment_left)
                pt.paid_amount += payable_amount
                pt.save()
                payment_left -= payable_amount

            messages.success(request, 'Payment submitted successfully.')
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'redirect_url': reverse('billing:payment_invoice', args=[payment.id])})
            return redirect('billing:payment_invoice', payment_id=payment.id)

    context = {
        'members': members_page,
        'query': query,
        'from_date': from_date,
        'to_date': to_date,
        'follow_up_date': follow_up_date_filter,
    }
    return render(request, 'billing/submit_due.html', context)

@login_required
def update_follow_up(request, member_id):
    gym = getattr(request, 'gym', None)
    if request.method == 'POST':
        follow_up_date_str = request.POST.get('follow_up_date')
        if follow_up_date_str:
            try:
                follow_up_date = date.fromisoformat(follow_up_date_str)
                member = get_object_or_404(Member, id=member_id, gym=gym)
                
                # Create a new payment record for the follow-up
                Payment.objects.create(
                    member=member,
                    amount=0,  # No payment is being made, this is just for the follow-up
                    payment_mode='other', 
                    comment=f"Follow-up date updated to {follow_up_date_str}",
                    follow_up_date=follow_up_date,
                    gym=gym
                )

                messages.success(request, f"Follow-up date for {member.first_name} {member.last_name} has been updated.")
            except (ValueError, TypeError):
                messages.error(request, "Invalid date format.")
        else:
            messages.error(request, "No follow-up date provided.")
    
    return redirect('billing:submit_due')


@never_cache
@login_required(login_url='login')
def payment_invoice(request, payment_id):
    gym = getattr(request, 'gym', None)
    payment = get_object_or_404(Payment, id=payment_id, gym=gym)
    context = {
        'payment': payment,
    }
    return render(request, 'billing/payment_invoice.html', context)


@never_cache
@login_required(login_url='login')
def invoice(request, member_id, history_id):
    gym = getattr(request, 'gym', None)
    member = get_object_or_404(Member, id=member_id, gym=gym)
    history = get_object_or_404(MembershipHistory, id=history_id, gym=gym)

    # Get all invoices for the member to find the next and previous
    member_invoices = list(MembershipHistory.objects.filter(member=member, gym=gym).order_by('created_at'))
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
    gym = getattr(request, 'gym', None)
    member = get_object_or_404(Member, id=member_id, gym=gym)
    pt_invoice = get_object_or_404(PersonalTrainer, id=pt_invoice_id, gym=gym)

    # Get all PT invoices for the member to find the next and previous
    member_pt_invoices = list(PersonalTrainer.objects.filter(member=member, gym=gym).order_by('created_at'))
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
    gym = getattr(request, 'gym', None)
    # Get query parameters
    query = request.GET.get('q', '')  # Default to an empty string
    status_filter = request.GET.get('status')
    sort_by = request.GET.get('sort', '-date')

    # Fetch membership invoices
    membership_invoices = MembershipHistory.objects.select_related('member', 'plan').filter(status='active', gym=gym).annotate(
        date=F('created_at'),
        type=Value('membership', output_field=models.CharField()),
        amount=F('total_amount'),
        due_amount=F('total_amount') - F('paid_amount'),
        invoice_id=F('id'),
        plan_title=F('plan__title')
    ).values('invoice_id', 'date', 'type', 'amount', 'member_id', 'member__member_id', 'member__first_name', 'member__last_name', 'plan_title', 'due_amount')

    # Fetch personal training invoices
    pt_invoices = PersonalTrainer.objects.select_related('member', 'trainer').filter(status='active', gym=gym).annotate(
        date=F('created_at'),
        type=Value('pt', output_field=models.CharField()),
        amount=F('total_amount'),
        due_amount=F('total_amount') - F('paid_amount'),
        invoice_id=F('id'),
        plan_title=F('trainer__name')
    ).values('invoice_id', 'date', 'type', 'amount', 'member_id', 'member__member_id', 'member__first_name', 'member__last_name', 'plan_title', 'due_amount')

    # Fetch payment invoices
    payment_invoices = Payment.objects.select_related('member').filter(gym=gym).annotate(
        date=F('payment_date'),
        type=Value('payment', output_field=models.CharField()),
        plan_title=Value('N/A', output_field=models.CharField()),
        due_amount=Value(0, output_field=models.DecimalField()),
        invoice_id=F('id')
    ).values('invoice_id', 'date', 'type', 'amount', 'member_id', 'member__member_id', 'member__first_name', 'member__last_name', 'plan_title', 'due_amount')

    # Combine and sort invoices
    all_invoices = sorted(
        list(membership_invoices) + list(pt_invoices) + list(payment_invoices),
        key=lambda x: x['date'],
        reverse='-' in sort_by
    )

    # Filter out invoices with no member_id
    all_invoices = [inv for inv in all_invoices if inv.get('member_id')]

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
        elif status_filter == 'receipt':
            all_invoices = [inv for inv in all_invoices if inv['type'] == 'payment']
        elif status_filter == 'invoice':
            all_invoices = [inv for inv in all_invoices if inv['type'] in ['membership', 'pt']]

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

@login_required
def delete_invoice(request, invoice_type, invoice_id):
    gym = getattr(request, 'gym', None)
    if request.method == 'POST':
        try:
            if invoice_type == 'membership':
                invoice = get_object_or_404(MembershipHistory, id=invoice_id, gym=gym)
            elif invoice_type == 'pt':
                invoice = get_object_or_404(PersonalTrainer, id=invoice_id, gym=gym)
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid invoice type.'}, status=400)

            invoice.status = 'inactive'
            invoice.save()
            return JsonResponse({'status': 'success', 'message': 'Invoice deleted successfully.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    # Keep the old GET request logic for other purposes if needed, but it won't be used by the new delete button.
    if invoice_type == 'membership':
        invoice = get_object_or_404(MembershipHistory, id=invoice_id, gym=gym)
    elif invoice_type == 'pt':
        invoice = get_object_or_404(PersonalTrainer, id=invoice_id, gym=gym)
    else:
        messages.error(request, 'Invalid invoice type.')
        return redirect('billing:invoices_list')

    invoice.status = 'inactive'
    invoice.save()
    messages.success(request, 'Invoice deleted successfully.')
    return redirect('billing:invoices_list')

@login_required
def trash_invoices(request):
    gym = getattr(request, 'gym', None)
    # Fetch inactive membership invoices
    membership_invoices = MembershipHistory.objects.select_related('member', 'plan').filter(status='inactive', gym=gym).annotate(
        date=F('created_at'),
        type=Value('membership', output_field=models.CharField()),
        amount=F('total_amount'),
        due_amount=F('total_amount') - F('paid_amount'),
        invoice_id=F('id'),
        plan_title=F('plan__title')
    ).values('invoice_id', 'date', 'type', 'amount', 'member_id', 'member__member_id', 'member__first_name', 'member__last_name', 'plan_title', 'due_amount')

    # Fetch inactive personal training invoices
    pt_invoices = PersonalTrainer.objects.select_related('member', 'trainer').filter(status='inactive', gym=gym).annotate(
        date=F('created_at'),
        type=Value('pt', output_field=models.CharField()),
        amount=F('total_amount'),
        due_amount=F('total_amount') - F('paid_amount'),
        invoice_id=F('id'),
        plan_title=F('trainer__name')
    ).values('invoice_id', 'date', 'type', 'amount', 'member_id', 'member__member_id', 'member__first_name', 'member__last_name', 'plan_title', 'due_amount')

    all_invoices = list(membership_invoices) + list(pt_invoices)

    # Sort by date
    all_invoices.sort(key=lambda x: x['date'], reverse=True)

    # Pagination
    paginator = Paginator(all_invoices, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'billing/trash.html', {'invoices': page_obj})

@login_required
def restore_invoice(request, invoice_type, invoice_id):
    gym = getattr(request, 'gym', None)
    if invoice_type == 'membership':
        invoice = get_object_or_404(MembershipHistory, id=invoice_id, gym=gym)
    elif invoice_type == 'pt':
        invoice = get_object_or_404(PersonalTrainer, id=invoice_id, gym=gym)
    else:
        messages.error(request, 'Invalid invoice type.')
        return redirect('billing:trash_invoices')

    invoice.status = 'active'
    invoice.save()
    messages.success(request, 'Invoice restored successfully.')
    return redirect('billing:trash_invoices')

@login_required
def delete_permanently(request, invoice_type, invoice_id):
    gym = getattr(request, 'gym', None)
    if invoice_type == 'membership':
        invoice = get_object_or_404(MembershipHistory, id=invoice_id, gym=gym)
    elif invoice_type == 'pt':
        invoice = get_object_or_404(PersonalTrainer, id=invoice_id, gym=gym)
    else:
        messages.error(request, 'Invalid invoice type.')
        return redirect('billing:trash_invoices')

    invoice.delete()
    messages.success(request, 'Invoice deleted permanently.')
    return redirect('billing:trash_invoices')