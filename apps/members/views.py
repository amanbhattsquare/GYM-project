from django.shortcuts import render, redirect, get_object_or_404
from .forms import MemberForm, MedicalHistoryForm, EmergencyContactForm
from .models import Member, MedicalHistory, EmergencyContact
from django.forms import modelformset_factory
from django.contrib import messages

def add_new_member(request):
    MedicalHistoryFormSet = modelformset_factory(MedicalHistory, form=MedicalHistoryForm, extra=1)
    if request.method == 'POST':
        member_form = MemberForm(request.POST, request.FILES)
        medical_formset = MedicalHistoryFormSet(request.POST, request.FILES, prefix='medical')
        emergency_form = EmergencyContactForm(request.POST, prefix='emergency')
        if member_form.is_valid() and medical_formset.is_valid() and emergency_form.is_valid():
            member = member_form.save()
            for form in medical_formset:
                if form.cleaned_data:
                    medical_history = form.save(commit=False)
                    medical_history.member = member
                    medical_history.save()
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

def member_profile(request, member_id):
    member = Member.objects.get(id=member_id)
    return render(request, 'members/member_profile.html', {'member': member})



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
            
            # Handle deletion of forms
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

from django.core.paginator import Paginator


from django.db.models import Q

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

def delete_member(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    member.delete()
    return redirect('member_list')