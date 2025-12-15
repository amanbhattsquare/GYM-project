from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import User
from .forms import GymForm, GymAdminForm, SubscriptionPlanForm
from .models import Gym, GymAdmin, SubscriptionPlan, GymSubscription
from apps.members.models import Member, MembershipHistory
from apps.billing.models import Payment
from django.db.models import Q, Sum
from django.contrib.auth.decorators import login_required
from .decorators import superadmin_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Sum, OuterRef, Subquery, F
from apps.billing.models import Payment
from decimal import Decimal
from datetime import date, timedelta

@login_required
@superadmin_required
def dashboard(request):
    total_gyms = Gym.objects.count()
    total_members = Member.objects.count()
    active_subscriptions = MembershipHistory.objects.filter(status='active').count()

    context = {
        'total_gyms': total_gyms,
        'total_members': total_members,
        'active_subscriptions': active_subscriptions,
    }
    return render(request, 'superadmin/dashboard.html', context)


@login_required
@superadmin_required
def add_gym(request):
    if request.method == 'POST':
        form = GymForm(request.POST, request.FILES)
        if form.is_valid():
            gym = form.save()
            messages.success(request, f"Gym '{gym.name}' has been added successfully.")
            return redirect('superadmin:create_gym_admin', gym_id=gym.id)
    else:
        form = GymForm()
    return render(request, 'superadmin/add_gym.html', {'form': form, 'page_title': 'Add Gym', 'button_text': 'Add Gym'})


@login_required
@superadmin_required
def create_gym_admin(request, gym_id):
    gym = get_object_or_404(Gym, id=gym_id)
    if request.method == 'POST':
        form = GymAdminForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            user.is_staff = True
            user.save()

            gym_admin = GymAdmin.objects.create(
                user=user,
                gym=gym,
                name=form.cleaned_data['name'],
                Phone_number=form.cleaned_data['Phone_number'],
                Department=form.cleaned_data.get('Department'),
                notes=form.cleaned_data.get('notes')
            )

            if 'photo' in request.FILES:
                gym_admin.photo = request.FILES['photo']
                gym_admin.save()

            messages.success(request, f"Admin for '{gym.name}' has been created successfully.")
            return redirect('superadmin:gym_list')
    else:
        form = GymAdminForm()
    return render(request, 'superadmin/create_gym_admin.html', {'form': form, 'gym': gym})



@login_required
@superadmin_required
def gym_list(request):
    query = request.GET.get('q')
    if query:
        gyms = Gym.objects.filter(
            Q(name__icontains=query) |
            Q(gym_id__icontains=query) |
            Q(address__icontains=query) |
            Q(admin_name__icontains=query)
        ).distinct()
    else:
        gyms = Gym.objects.all()

    for gym in gyms:
        admin = GymAdmin.objects.filter(gym=gym).first()
        if admin:
            gym.has_admin = True
            gym.admin_name = admin.user.get_full_name() or admin.user.username
            gym.admin_username = admin.user.username
        else:
            gym.has_admin = False
            gym.admin_name = "N/A"
            gym.admin_username = "N/A"

    paginator = Paginator(gyms, 10)  # Show 10 gyms per page
    page = request.GET.get('page')
    gyms = paginator.get_page(page)

    return render(request, 'superadmin/gym_list.html', {'gyms': gyms})


@login_required
@superadmin_required
def update_gym(request, gym_id):
    gym = get_object_or_404(Gym, pk=gym_id)
    if request.method == 'POST':
        form = GymForm(request.POST, request.FILES, instance=gym)
        if form.is_valid():
            gym = form.save()
            messages.success(request, f"Gym '{gym.name}' has been updated successfully.")
            return redirect('superadmin:gym_list')
    else:
        form = GymForm(instance=gym)
    return render(request, 'superadmin/add_gym.html', {'form': form, 'page_title': 'Update Gym', 'button_text': 'Update Gym'})

@login_required
@superadmin_required
@require_POST
def delete_gym(request, gym_id):
    gym = get_object_or_404(Gym, pk=gym_id)
    try:
        gym.delete()
        messages.success(request, 'Gym has been deleted successfully.')
        return JsonResponse({'status': 'success', 'message': 'Gym deleted successfully.'})
    except Exception as e:
        messages.error(request, f'An error occurred: {e}')
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
@superadmin_required
def gym_profile(request, gym_id):
    gym = get_object_or_404(Gym, pk=gym_id)
    form = GymForm(instance=gym)

    # Paginate payment history
    payment_list = Payment.objects.filter(gym=gym).order_by('-payment_date')
    paginator_payments = Paginator(payment_list, 10)  # Show 10 payments per page
    page_payments = request.GET.get('page_payments')
    try:
        payment_history = paginator_payments.page(page_payments)
    except PageNotAnInteger:
        payment_history = paginator_payments.page(1)
    except EmptyPage:
        payment_history = paginator_payments.page(paginator_payments.num_pages)

    gym_subscriptions = GymSubscription.objects.filter(gym=gym)
    active_subscription = gym_subscriptions.filter(start_date__lte=date.today(), end_date__gte=date.today()).first()
    gym_admins = GymAdmin.objects.filter(gym=gym)
    admin_form = GymAdminForm()

    # Calculate due amount
    aggregation = gym_subscriptions.aggregate(
        total_amount=Sum('total_amount'),
        paid_amount=Sum('paid_amount')
    )
    due_amount = (aggregation['total_amount'] or 0) - (aggregation['paid_amount'] or 0)

    return render(request, 'superadmin/gym_profile.html', {
        'gym': gym,
        'form': form,
        'payment_history': payment_history,
        'gym_subscriptions': gym_subscriptions,
        'active_subscription': active_subscription,
        'gym_admins': gym_admins,
        'admin_form': admin_form,
        'due_amount': due_amount
    })

@login_required
@superadmin_required
def reset_admin_password(request, admin_id):
    gym_admin = get_object_or_404(GymAdmin, pk=admin_id)
    if request.method == 'POST':
        form = GymAdminForm(request.POST)
        if form.is_valid():
            user = gym_admin.user
            password = form.cleaned_data['password']
            user.set_password(password)
            user.save()
            return redirect('superadmin:gym_profile', gym_id=gym_admin.gym.id)
    return redirect('superadmin:gym_profile', gym_id=gym_admin.gym.id)


@login_required
@superadmin_required
def subscription_plan_list(request):
    query = request.GET.get('q')
    if query:
        plans = SubscriptionPlan.objects.filter(
            Q(name__icontains=query) |
            Q(price__icontains=query) |
            Q(duration_months__icontains=query)
        ).distinct()
    else:
        plans = SubscriptionPlan.objects.all()
    return render(request, 'superadmin/subscription_plan_list.html', {'plans': plans})

from django.contrib import messages

@login_required
@superadmin_required
def add_subscription_plan(request):
    if request.method == 'POST':
        form = SubscriptionPlanForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Subscription plan created successfully.")
            return redirect('superadmin:subscription_plan_list')
    else:
        form = SubscriptionPlanForm()
    return render(request, 'superadmin/add_subscription_plan.html', {'form': form})

@login_required
@superadmin_required
def update_subscription_plan(request, plan_id):
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)
    if request.method == 'POST':
        form = SubscriptionPlanForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()
            return redirect('superadmin:subscription_plan_list')
    else:
        form = SubscriptionPlanForm(instance=plan)
    return render(request, 'superadmin/update_subscription_plan.html', {'form': form})

@login_required
@superadmin_required
@require_POST
def delete_subscription_plan(request, plan_id):
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)
    try:
        plan.delete()
        messages.success(request, 'Subscription plan has been deleted successfully.')
        return JsonResponse({'status': 'success', 'message': 'Subscription plan deleted successfully.'})
    except Exception as e:
        messages.error(request, f'An error occurred: {e}')
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
@superadmin_required
def assign_subscription(request):
    if request.method == 'POST':
        gym_id = request.POST.get('gym')
        subscription_id = request.POST.get('subscription')
        start_date = request.POST.get('start_date')
        discount = request.POST.get('discount')
        total_amount = request.POST.get('total_amount')
        paid_amount = request.POST.get('paid_amount')
        payment_mode = request.POST.get('payment_mode')
        transaction_id = request.POST.get('transaction_id')
        remark = request.POST.get('remark')

        gym = get_object_or_404(Gym, id=gym_id)
        subscription = get_object_or_404(SubscriptionPlan, id=subscription_id)

        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = start_date_obj + timedelta(days=subscription.duration_months * 30)

        GymSubscription.objects.create(
            gym=gym,
            subscription=subscription,
            start_date=start_date,
            end_date=end_date,
            discount=discount,
            total_amount=total_amount,
            paid_amount=paid_amount,
            payment_mode=payment_mode,
            transaction_id=transaction_id,
            remark=remark
        )
        messages.success(request, f'Subscription assigned to {gym.name} successfully.')
        return redirect('superadmin:gym_list')

    else:
        gyms = Gym.objects.all()
        subscriptions = SubscriptionPlan.objects.all()
        return render(request, 'superadmin/assign_subscription.html', {
            'gyms': gyms,
            'subscriptions': subscriptions
        })


@login_required
@superadmin_required
def billing_history(request):
    query = request.GET.get('q')
    status_filter = request.GET.get('status')
    type_filter = request.GET.get('type')

    base_queryset = GymSubscription.objects.all() if request.user.is_superuser else GymSubscription.objects.filter(gym=request.user.gymadmin.gym)

    subscriptions = base_queryset.annotate(
        due_amount_calculated=F('total_amount') - F('paid_amount')
    ).order_by('-start_date')

    if query:
        subscriptions = subscriptions.filter(gym__name__icontains=query)

    if status_filter:
        if status_filter == 'paid':
            subscriptions = subscriptions.filter(due_amount_calculated=0)
        elif status_filter == 'unpaid':
            subscriptions = subscriptions.filter(due_amount_calculated__gt=0)

    payments = Payment.objects.filter(gym__in=subscriptions.values('gym')).order_by('-payment_date')

    if type_filter == 'subscription':
        history = list(subscriptions)
    elif type_filter == 'payment':
        history = list(payments)
    else:
        history = sorted(
            list(subscriptions) + list(payments),
            key=lambda item: item.start_date if isinstance(item, GymSubscription) else item.payment_date.date(),
            reverse=True
        )

    paginator = Paginator(history, 10)
    page = request.GET.get('page')
    try:
        history_page = paginator.page(page)
    except PageNotAnInteger:
        history_page = paginator.page(1)
    except EmptyPage:
        history_page = paginator.page(paginator.num_pages)

    context = {
        'history': history_page,
        'query': query,
        'status_filter': status_filter,
        'type_filter': type_filter,
    }
    return render(request, 'superadmin/billing_history.html', context)


@login_required
@superadmin_required
def submit_due(request):
    if request.method == 'POST':
        gym_id = request.POST.get('gym')
        amount_to_pay = request.POST.get('amount_to_pay')
        payment_method = request.POST.get('payment_method')
        notes = request.POST.get('notes')
        
        if gym_id and amount_to_pay:
            gym = get_object_or_404(Gym, id=gym_id)
            amount_to_pay_decimal = Decimal(amount_to_pay)

            # Total due for the gym
            aggregation = GymSubscription.objects.filter(gym=gym).aggregate(
                total_amount=Sum('total_amount'),
                paid_amount=Sum('paid_amount')
            )
            gym_total_due = (aggregation['total_amount'] or 0) - (aggregation['paid_amount'] or 0)

            if amount_to_pay_decimal > gym_total_due:
                messages.error(request, 'Amount to pay cannot be greater than the total due amount.')
            else:
                # Apply payment to subscriptions, oldest first
                subscriptions = GymSubscription.objects.filter(gym=gym).annotate(
                    due=F('total_amount') - F('paid_amount')
                ).filter(due__gt=0).order_by('start_date')
                
                payment_to_apply = amount_to_pay_decimal
                for sub in subscriptions:
                    if payment_to_apply <= 0:
                        break
                    
                    current_due = sub.total_amount - sub.paid_amount
                    payable = min(payment_to_apply, current_due)
                    sub.paid_amount += payable
                    sub.save()
                    payment_to_apply -= payable

                Payment.objects.create(
                    gym=gym,
                    amount=amount_to_pay_decimal,
                    payment_date=date.today(),
                    payment_mode=payment_method,
                    comment=notes
                )
                messages.success(request, 'Due amount submitted successfully.')
        
        return redirect('superadmin:submit_due')

    gyms_with_due = Gym.objects.annotate(
        total_subscription_amount=Sum('gymsubscription__total_amount'),
        total_paid_amount=Sum('gymsubscription__paid_amount')
    ).filter(total_subscription_amount__gt=F('total_paid_amount')).annotate(
        total_due=F('total_subscription_amount') - F('total_paid_amount'),
        admin_name=F('gymadmin__name'),
        contact_no=F('phone'),
    )

    query = request.GET.get('q')
    if query:
        gyms_with_due = gyms_with_due.filter(
            Q(name__icontains=query) |
            Q(gym_id__icontains=query) |
            Q(admin_name__icontains=query)
        ).distinct()

    return render(request, 'superadmin/submit_due.html', {'gyms': gyms_with_due, 'query': query})

@login_required
@superadmin_required
def get_due_amount(request, gym_id):
    gym = get_object_or_404(Gym, id=gym_id)
    aggregation = GymSubscription.objects.filter(gym=gym).aggregate(
        total_amount=Sum('total_amount'),
        paid_amount=Sum('paid_amount')
    )
    due_amount = (aggregation['total_amount'] or 0) - (aggregation['paid_amount'] or 0)
    return JsonResponse({'due_amount': due_amount})