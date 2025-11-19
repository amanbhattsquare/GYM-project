from django.shortcuts import render, redirect, get_object_or_404
from .forms import MemberForm, MedicalHistoryForm, EmergencyContactForm, MembershipHistoryForm
from .models import Member, MedicalHistory, EmergencyContact, MembershipHistory
from apps.management.models import MembershipPlan
from django.forms import modelformset_factory
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.core.serializers import serialize
from django.views.decorators.http import require_POST

from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache


@never_cache
@login_required(login_url='login')
def add_new_member(request):
    MedicalHistoryFormSet = modelformset_factory(MedicalHistory, form=MedicalHistoryForm, extra=1, can_delete=True)
    if request.method == 'POST':
        member_form = MemberForm(request.POST, request.FILES)
        medical_formset = MedicalHistoryFormSet(request.POST, request.FILES, prefix='medical')
        emergency_form = EmergencyContactForm(request.POST, prefix='emergency')
        if member_form.is_valid() and medical_formset.is_valid() and emergency_form.is_valid():
            member = member_form.save()
            
            instances = medical_formset.save(commit=False)
            for instance in instances:
                instance.member = member
                instance.save()
            
            medical_formset.save_m2m() 
            
            for form in medical_formset.deleted_forms:
                if form.instance.pk:
                    form.instance.delete()

            emergency_contact = emergency_form.save(commit=False)
            emergency_contact.member = member
            emergency_contact.save()
            messages.success(request, 'Member added successfully!')
            return redirect('member_list')
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
    member = Member.objects.get(id=member_id)
    membership_histories = MembershipHistory.objects.filter(member=member).order_by('-created_at')
    latest_membership = membership_histories.first()
    return render(request, 'members/member_profile.html', {
        'member': member, 
        'membership_histories': membership_histories,
        'membership_history': latest_membership
        })



@never_cache
@login_required(login_url='login')
def edit_member(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    try:
        emergency_contact = member.emergency_contact
    except EmergencyContact.DoesNotExist:
        emergency_contact = None

    MedicalHistoryFormSet = modelformset_factory(MedicalHistory, form=MedicalHistoryForm, extra=1, can_delete=True)

    if request.method == 'POST':
        form = MemberForm(request.POST, request.FILES, instance=member)
        medical_formset = MedicalHistoryFormSet(request.POST, request.FILES, queryset=MedicalHistory.objects.filter(member=member), prefix='medical')
        emergency_form = EmergencyContactForm(request.POST, instance=emergency_contact, prefix='emergency')

        if form.is_valid() and medical_formset.is_valid() and emergency_form.is_valid():
            form.save()
            
            instances = medical_formset.save(commit=False)
            for instance in instances:
                instance.member = member
                instance.save()
            
            medical_formset.save_m2m()

            for form_in_formset in medical_formset.deleted_forms:
                if form_in_formset.instance.pk:
                    form_in_formset.instance.delete()

            emergency_contact_instance = emergency_form.save(commit=False)
            emergency_contact_instance.member = member
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
        medical_formset = MedicalHistoryFormSet(queryset=MedicalHistory.objects.filter(member=member), prefix='medical')
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
    member_list = Member.objects.all()
    query = request.GET.get('q')
    if query:
        member_list = member_list.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(mobile_number__icontains=query)
        ).distinct()

    paginator = Paginator(member_list, 10)  # Show 10 members per page.

    page_number = request.GET.get('page')
    members = paginator.get_page(page_number)
    return render(request, 'members/member_list.html', {'members': members})

@require_POST
def delete_member(request, member_id):
    member = get_object_or_404(Member, id=member_id)
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
    member = get_object_or_404(Member, id=member_id)
    plans = MembershipPlan.objects.all()
    plans_json = serialize('json', plans)
    if request.method == 'POST':
        form = MembershipHistoryForm(request.POST)
        if form.is_valid():
            history = form.save(commit=False)
            history.member = member
            history.save()
            member.membership_plan = history.plan
            member.save()
            messages.success(request, f'Membership plan "{history.plan.title}" assigned to {member.first_name} {member.last_name}.')
            return redirect('invoice', member_id=member.id, history_id=history.id)
    else:
        form = MembershipHistoryForm()
    return render(request, 'members/membership_plan_assign.html', {'member': member, 'plans': plans, 'plans_json': plans_json, 'form': form})

@never_cache
@login_required(login_url='login')
def invoice(request, member_id, history_id):
    member = get_object_or_404(Member, id=member_id)
    history = get_object_or_404(MembershipHistory, id=history_id)
    return render(request, 'members/invoice.html', {'member': member, 'history': history})