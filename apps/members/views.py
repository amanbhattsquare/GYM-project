from django.shortcuts import render, redirect, get_object_or_404
from .forms import MemberForm, MedicalHistoryForm, EmergencyContactForm, MembershipHistoryForm, PersonalTrainerForm
from .models import Member, MedicalHistory, EmergencyContact, MembershipHistory, PersonalTrainer, MembershipFreeze
from apps.management.models import MembershipPlan
from apps.trainers.models import Trainer
from apps.billing.models import Payment
from django.forms import modelformset_factory
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum, F, ExpressionWrapper, DecimalField, Value
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.core.serializers import serialize
from django.views.decorators.http import require_POST

from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.utils import timezone


@never_cache
@login_required(login_url='login')
def add_new_member(request):
    gym = getattr(request, 'gym', None)
    
    MedicalHistoryFormSet = modelformset_factory(MedicalHistory, form=MedicalHistoryForm, extra=1, can_delete=True)
    if request.method == 'POST':
        member_form = MemberForm(request.POST, request.FILES)
        medical_formset = MedicalHistoryFormSet(request.POST, request.FILES, prefix='medical')
        emergency_form = EmergencyContactForm(request.POST, prefix='emergency')
        if member_form.is_valid() and medical_formset.is_valid() and emergency_form.is_valid():
            member = member_form.save(commit=False)
            member.gym = gym
            member.save()
            
            instances = medical_formset.save(commit=False)
            for instance in instances:
                instance.member = member
                instance.gym = gym
                instance.save()
            
            medical_formset.save_m2m() 
            
            for form in medical_formset.deleted_forms:
                if form.instance.pk:
                    form.instance.delete()

            emergency_contact = emergency_form.save(commit=False)
            emergency_contact.member = member
            emergency_contact.gym = gym
            emergency_contact.save()
            messages.success(request, 'Member added successfully!')
            return redirect('assign_membership_plan', member_id=member.id)
        else:
            print("Member form errors:", member_form.errors)
            print("Medical formset errors:", medical_formset.errors)
            print("Emergency form errors:", emergency_form.errors)
    else:
        member_form = MemberForm()
        medical_formset = MedicalHistoryFormSet(queryset=MedicalHistory.objects.none(), prefix='medical')
        emergency_form = EmergencyContactForm(prefix='emergency')
    return render(request, 'members/add_new_member.html', {
        'form': member_form,
        'medical_formset': medical_formset,
        'emergency_form': emergency_form
    })

@never_cache
@login_required(login_url='login')
def member_profile(request, member_id):
    gym = getattr(request, 'gym', None)
    member = get_object_or_404(Member, id=member_id, gym=gym)
    
    # Fetch both active and frozen memberships
    membership_histories = MembershipHistory.objects.filter(
        member=member, status__in=['active', 'frozen'], gym=gym
    ).order_by('-id')
    
    pt_member = PersonalTrainer.objects.select_related('trainer').filter(
        member=member, status='active', gym=gym
    ).order_by('-id')
    
    # The latest membership can be active or frozen
    latest_membership = membership_histories.first()
    
    payments = Payment.objects.filter(member=member, gym=gym).order_by('-payment_date')

    # Calculate the total due amount for active memberships only
    membership_due_amount = membership_histories.filter(status='active').aggregate(
        total_due=Sum(F('total_amount') - F('paid_amount'))
    )['total_due'] or 0

    # Calculate the total due amount for personal training
    pt_due_amount = pt_member.filter(status='active').aggregate(
        total_due=Sum(F('total_amount') - F('paid_amount'))
    )['total_due'] or 0

    total_due_amount = membership_due_amount + pt_due_amount

    return render(request, 'members/member_profile.html', {
        'member': member, 
        'membership_histories': membership_histories,
        'pt_member': pt_member,
        'membership_history': latest_membership,
        'due_amount': total_due_amount,
        'pt_invoices': pt_member,
        'payments': payments,
        'membership_plan': latest_membership.plan if latest_membership else None
    })


@never_cache
@login_required(login_url='login')
def edit_member(request, member_id):
    gym = getattr(request, 'gym', None)
    member = get_object_or_404(Member, id=member_id, gym=gym)
    try:
        emergency_contact = member.emergency_contact
    except EmergencyContact.DoesNotExist:
        emergency_contact = None

    MedicalHistoryFormSet = modelformset_factory(MedicalHistory, form=MedicalHistoryForm, extra=1, can_delete=True)

    if request.method == 'POST':
        form = MemberForm(request.POST, request.FILES, instance=member)
        medical_formset = MedicalHistoryFormSet(request.POST, request.FILES, queryset=MedicalHistory.objects.filter(member=member, gym=gym), prefix='medical')
        emergency_form = EmergencyContactForm(request.POST, instance=emergency_contact, prefix='emergency')

        if form.is_valid() and medical_formset.is_valid() and emergency_form.is_valid():
            form.save()
            
            instances = medical_formset.save(commit=False)
            for instance in instances:
                instance.member = member
                instance.gym = gym
                instance.save()
            
            medical_formset.save_m2m()

            for form_in_formset in medical_formset.deleted_forms:
                if form_in_formset.instance.pk:
                    form_in_formset.instance.delete()

            emergency_contact_instance = emergency_form.save(commit=False)
            emergency_contact_instance.member = member
            emergency_contact_instance.gym = gym
            emergency_contact_instance.save()
            
            messages.success(request, 'Member details updated successfully!')
            return redirect('member_list')
        else:
            # For debugging purposes
            print("Member form errors:", form.errors)
            print("Medical formset errors:", medical_formset.errors)
            print("Emergency form errors:", emergency_form.errors)

    else:
        form = MemberForm(instance=member)
        medical_formset = MedicalHistoryFormSet(queryset=MedicalHistory.objects.filter(member=member, gym=gym), prefix='medical')
        emergency_form = EmergencyContactForm(instance=emergency_contact, prefix='emergency')

    return render(request, 'members/edit_member.html', {
        'form': form,
        'medical_formset': medical_formset,
        'emergency_form': emergency_form,
        'member': member
    })


@never_cache
@login_required(login_url='login') 
def member_list(request):
    gym = getattr(request, 'gym', None)
    member_list = Member.objects.filter(gym=gym).order_by('-id')
    query = request.GET.get('q')
    if query:
        member_list = member_list.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(mobile_number__icontains=query)
        ).distinct()

    for member in member_list:
        membership_due_amount = member.membership_history.filter(status='active').aggregate(
            total_due=Sum(F('total_amount') - F('paid_amount'))
        )['total_due'] or 0
        pt_due_amount = member.personal_trainer.filter(status='active').aggregate(
            total_due=Sum(F('total_amount') - F('paid_amount'))
        )['total_due'] or 0
        member.total_due = membership_due_amount + pt_due_amount
        latest_history = member.membership_history.filter(gym=gym).order_by('-id').first()
        member.latest_membership_history = latest_history

    paginator = Paginator(member_list, 10)  # Show 10 members per page.

    page_number = request.GET.get('page')
    members = paginator.get_page(page_number)
    return render(request, 'members/member_list.html', {'members': members})

@require_POST
def toggle_member_status(request, member_id):
    gym = getattr(request, 'gym', None)
    member = get_object_or_404(Member, id=member_id, gym=gym)
    if member.status == 'active':
        member.status = 'inactive'
    else:
        member.status = 'active'
    member.save()
    messages.success(request, f'Member status has been updated to {member.status}.')
    return JsonResponse({'status': 'success', 'message': 'Member status updated successfully.', 'new_status': member.status})

@require_POST
def delete_member(request, member_id):
    gym = getattr(request, 'gym', None)
    member = get_object_or_404(Member, id=member_id, gym=gym)
    try:
        member.delete()
        messages.success(request, 'Member has been deleted successfully.')
        return JsonResponse({'status': 'success', 'message': 'Member deleted successfully.'})
    except Exception as e:
        messages.error(request, f'An error occurred: {e}')
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@never_cache
@login_required(login_url='login')
def assign_membership_plan(request, member_id):
    gym = getattr(request, 'gym', None)
    member = get_object_or_404(Member, id=member_id, gym=gym)
    plans = MembershipPlan.objects.filter(gym=gym)
    plans_json = serialize('json', plans)
    if request.method == 'POST':
        form = MembershipHistoryForm(request.POST, gym=gym)
        if form.is_valid():
            history = form.save(commit=False)
            history.member = member
            history.gym = gym
            history.transaction_id = request.POST.get('transaction_id')
            history.save()

            if history.paid_amount > 0:
                Payment.objects.create(
                    gym=gym,
                    member=member,
                    amount=history.paid_amount,
                    payment_mode=history.payment_mode,
                    transaction_id=history.transaction_id,
                    comment=f"Initial payment for {history.plan.title}"
                )

            member.membership_plan = history.plan
            member.save()
            messages.success(request, f'Membership plan "{history.plan.title}" assigned to {member.first_name} {member.last_name}.')
            return redirect('billing:invoice', member_id=member.id, history_id=history.id)
    else:
        form = MembershipHistoryForm(gym=gym)
    return render(request, 'members/membership_plan_assign.html', {'member': member, 'plans': plans, 'plans_json': plans_json, 'form': form})

@never_cache
@login_required(login_url='login')
def assign_pt_trainer(request, member_id):
    gym = getattr(request, 'gym', None) 
    member = get_object_or_404(Member, id=member_id, gym=gym)
    
    # Filter trainers by the current gym
    trainers = Trainer.objects.filter(gym=gym)
    trainers_json = serialize('json', trainers)
    
    if request.method == 'POST':
        form = PersonalTrainerForm(request.POST, gym=gym) # Pass gym to the form
        if form.is_valid():
            pt_assignment = form.save(commit=False)
            pt_assignment.member = member
            pt_assignment.gym = gym # Assign gym to the instance
            pt_assignment.transaction_id = request.POST.get('transaction_id')
            pt_assignment.save()
            messages.success(request, f'Personal Trainer "{pt_assignment.trainer.name}" assigned to {member.first_name} {member.last_name}.')
            return redirect('billing:pt_invoice', member_id=member.id, pt_invoice_id=pt_assignment.id)
    else:
        form = PersonalTrainerForm(gym=gym) # Pass gym to the form
    
    return render(request, 'members/assign_PT_trainer.html', {'member': member, 'trainers': trainers, 'trainers_json': trainers_json, 'form': form})


@login_required(login_url='login')
def unfreeze_membership(request, membership_id):
    membership = get_object_or_404(MembershipHistory, id=membership_id)
    
    if request.method == 'POST':
        freeze = MembershipFreeze.objects.filter(membership=membership, unfreeze_date__isnull=True).first()
        if freeze:
            freeze.unfreeze_date = timezone.now().date()
            freeze.save()
            
            membership.status = 'active'
            membership.save()
            
            messages.success(request, "Membership has been unfrozen.")
        else:
            messages.error(request, "No active freeze found for this membership.")
        
        return redirect('member_profile', member_id=membership.member.id)
    
    return redirect('member_profile', member_id=membership.member.id)


@login_required(login_url='login')
def freeze_membership(request, membership_id):
    membership = get_object_or_404(MembershipHistory, id=membership_id)
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        
        # Check if the membership is already frozen
        if membership.is_frozen:
            messages.error(request, "This membership is already frozen.")
            return redirect('member_profile', member_id=membership.member.id)

        MembershipFreeze.objects.create(
            membership=membership,
            freeze_date=timezone.now().date(),
            reason=reason
        )
        
        membership.status = 'frozen'
        membership.save()
        
        messages.success(request, "Membership has been frozen.")
        return redirect('member_profile', member_id=membership.member.id)
    
    return redirect('member_profile', member_id=membership.member.id)