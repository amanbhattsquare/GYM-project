from django.shortcuts import render, redirect, get_object_or_404
from .forms import EnquiryForm
from .models import Enquiry
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache



@never_cache
@login_required(login_url='login')
def add_new_enquiry(request):
    if request.method == 'POST':
        form = EnquiryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Enquiry added successfully!')
            return redirect('enquiry_list')
    else:
        form = EnquiryForm()
    return render(request, 'enquiry/add_new_enquiry.html', {'form': form})
@never_cache
@login_required(login_url='login')
def enquiry_list(request):
    enquiry_list = Enquiry.objects.all()
    return render(request, 'enquiry/enquiry_list.html', {'enquiries': enquiry_list})

@never_cache
@login_required(login_url='login')
def edit_enquiry(request, enquiry_id):
    enquiry = get_object_or_404(Enquiry, id=enquiry_id)
    if request.method == 'POST':
        form = EnquiryForm(request.POST, instance=enquiry)
        if form.is_valid():
            form.save()
            messages.success(request, 'Enquiry updated successfully!')
            return redirect('enquiry_list')
    else:
        form = EnquiryForm(instance=enquiry)
    return render(request, 'enquiry/edit_enquiry.html', {'form': form})
@never_cache
@login_required(login_url='login')
def delete_enquiry(request, enquiry_id):
    enquiry = get_object_or_404(Enquiry, id=enquiry_id)
    enquiry.delete()
    messages.success(request, 'Enquiry deleted successfully!')
    return redirect('enquiry_list')