from django.shortcuts import render, get_object_or_404, redirect
from apps.members.models import Member, MembershipHistory, PersonalTrainer
from .models import Payment
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.db import models
from django.db.models import Q, Sum, F, Value, CharField, Case, When, DecimalField
from django.db.models.functions import Coalesce
from django.core.paginator import Paginator
from django.contrib import messages
from decimal import Decimal, ROUND_HALF_UP
from datetime import date
from django.http import JsonResponse
from django.urls import reverse




@never_cache
@login_required(login_url='login')
def submit_due(request):
    gym = getattr(request, 'gym', None)

    # Subquery for membership due
    membership_due_subquery = MembershipHistory.objects.filter(
        member=models.OuterRef('pk'),
        status='active',
        gym=gym
    ).values('member').annotate(
        total_due=Sum(F('total_amount') - F('paid_amount'))
    ).values('total_due')

    # Subquery for personal trainer due
    pt_due_subquery = PersonalTrainer.objects.filter(
        member=models.OuterRef('pk'),
        status='active',
        gym=gym
    ).values('member').annotate(
        total_due=Sum(F('total_amount') - F('paid_amount'))
    ).values('total_due')

    latest_follow_up = Payment.objects.filter(
        member=models.OuterRef('pk'),
        gym=gym
    ).order_by('-follow_up_date').values('follow_up_date')[:1]

    members_with_due = Member.objects.filter(gym=gym).annotate(
        membership_due=Coalesce(models.Subquery(membership_due_subquery, output_field=DecimalField()), Value(0, output_field=DecimalField())),
        pt_due=Coalesce(models.Subquery(pt_due_subquery, output_field=DecimalField()), Value(0, output_field=DecimalField())),
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

    context = {
        'members': members_page,
        'query': query,
        'from_date': from_date,
        'to_date': to_date,
        'follow_up_date': follow_up_date_filter,
    }
    return render(request, 'billing/submit_due.html', context)

@login_required
def pay_due_payment(request, member_id):
    gym = getattr(request, 'gym', None)
    member = get_object_or_404(Member, id=member_id, gym=gym)

    membership_invoices = MembershipHistory.objects.filter(member=member, status='active', gym=gym).exclude(paid_amount=F('total_amount')).annotate(due=F('total_amount') - F('paid_amount'))
    pt_invoices = PersonalTrainer.objects.filter(member=member, status='active', gym=gym).exclude(paid_amount=F('total_amount')).annotate(due=F('total_amount') - F('paid_amount'))

    if request.method == 'POST':
        invoice_type = request.POST.get('invoice_type')
        invoice_id = request.POST.get('invoice_id')
        amount_paid = Decimal(request.POST.get('amount_paid'))
        payment_mode = request.POST.get('payment_mode')
        transaction_id = request.POST.get('transaction_id')
        comment = request.POST.get('comment')

        invoice = None
        if invoice_type == 'membership':
            invoice = get_object_or_404(MembershipHistory, id=invoice_id, member=member, gym=gym)
        elif invoice_type == 'pt':
            invoice = get_object_or_404(PersonalTrainer, id=invoice_id, member=member, gym=gym)

        if invoice:
            due_amount = invoice.total_amount - invoice.paid_amount
            if amount_paid > due_amount:
                messages.error(request, f'Amount paid cannot be greater than the due amount of {due_amount}.')
            else:
                invoice.paid_amount += amount_paid
                invoice.save()

                Payment.objects.create(
                    member=member,
                    amount=amount_paid,
                    payment_mode=payment_mode,
                    transaction_id=transaction_id,
                    comment=comment,
                    gym=gym,
                    membership_history=invoice if invoice_type == 'membership' else None,
                    personal_trainer=invoice if invoice_type == 'pt' else None
                )
                messages.success(request, 'Payment submitted successfully.')

                if invoice_type == 'pt':
                    return redirect('billing:pt_invoice', member_id=member.id, pt_invoice_id=invoice.id)
                else:
                    return redirect('billing:submit_due')
        else:
            messages.error(request, 'Invalid invoice selected.')

    context = {
        'member': member,
        'membership_invoices': membership_invoices,
        'pt_invoices': pt_invoices,
    }
    return render(request, 'billing/pay_due_payment.html', context)

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
def invoice(request, member_id, history_id):
    gym = getattr(request, 'gym', None)
    member = get_object_or_404(Member, id=member_id, gym=gym)
    history = get_object_or_404(MembershipHistory, id=history_id, gym=gym)

    # Get all invoices for the member to find the next and previous
    member_invoices = list(MembershipHistory.objects.filter(member=member, gym=gym).order_by('created_at'))
    current_invoice_index = member_invoices.index(history)

    previous_invoice = member_invoices[current_invoice_index - 1] if current_invoice_index > 0 else None
    next_invoice = member_invoices[current_invoice_index + 1] if current_invoice_index < len(member_invoices) - 1 else None

    sgst = history.sgst
    cgst = history.cgst
    gst_amount = history.gst_amount

    sgst_rate = 0
    cgst_rate = 0
    if gym.gst_enabled:
        gst_rate = gym.gst_rate
        sgst_rate = gst_rate / 2
        cgst_rate = gst_rate / 2

    context = {
        'member': member,
        'history': history,
        'previous_invoice': previous_invoice,
        'next_invoice': next_invoice,
        'sgst': sgst,
        'cgst': cgst,
        'sgst_rate': sgst_rate,
        'cgst_rate': cgst_rate,
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
        'gym': gym
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
    membership_invoices = MembershipHistory.objects.select_related('member', 'plan').filter(gym=gym, is_deleted=False).annotate(
        date=F('created_at'),
        type=Value('membership', output_field=models.CharField()),
        amount=F('total_amount'),
        due_amount=F('total_amount') - F('paid_amount'),
        invoice_id=F('id'),
        plan_title=F('plan__title')
    ).values('invoice_id', 'date', 'type', 'amount', 'paid_amount', 'due_amount', 'member_id', 'member__member_id', 'member__first_name', 'member__last_name', 'plan_title')

    # Fetch personal training invoices
    pt_invoices = PersonalTrainer.objects.select_related('member', 'trainer').filter(gym=gym, is_deleted=False).annotate(
        date=F('created_at'),
        type=Value('pt', output_field=models.CharField()),
        amount=F('total_amount'),
        due_amount=F('total_amount') - F('paid_amount'),
        invoice_id=F('id'),
        plan_title=F('trainer__name')
    ).values('invoice_id', 'date', 'type', 'amount', 'member_id', 'member__member_id', 'member__first_name', 'member__last_name', 'plan_title', 'due_amount')

    # Combine and sort invoices
    all_invoices = sorted(
        list(membership_invoices) + list(pt_invoices),
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
            all_invoices = [inv for inv in all_invoices if inv['due_amount'] == 0]
        elif status_filter == 'unpaid':
            all_invoices = [inv for inv in all_invoices if inv['due_amount'] > 0]

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

            invoice.is_deleted = True
            invoice.save()
            return JsonResponse({'status': 'success', 'message': 'Invoice moved to trash successfully.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

@login_required
def trash_invoices(request):
    gym = getattr(request, 'gym', None)
    # Fetch inactive membership invoices
    membership_invoices = MembershipHistory.objects.select_related('member', 'plan').filter(gym=gym, is_deleted=True).annotate(
        date=F('created_at'),
        type=Value('membership', output_field=models.CharField()),
        amount=F('total_amount'),
        due_amount=F('total_amount') - F('paid_amount'),
        invoice_id=F('id'),
        plan_title=F('plan__title')
    ).values('invoice_id', 'date', 'type', 'amount', 'member_id', 'member__member_id', 'member__first_name', 'member__last_name', 'plan_title', 'due_amount')

    # Fetch inactive personal training invoices
    pt_invoices = PersonalTrainer.objects.select_related('member', 'trainer').filter(gym=gym, is_deleted=True).annotate(
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

    invoice.is_deleted = False
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