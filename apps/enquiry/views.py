from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from .models import Enquiry
from .forms import EnquiryForm
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.db.models import Q

@login_required
def update_enquiry_status(request, enquiry_id):
    enquiry = get_object_or_404(Enquiry, id=enquiry_id)
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in [choice[0] for choice in Enquiry.STATUS_CHOICES]:
            enquiry.status = status
            enquiry.save()
            messages.success(request, f"Status for {enquiry.name} updated successfully.")
    return redirect('enquiry_list')

@login_required
def add_new_enquiry(request):
    gym = getattr(request, 'gym', None)
    if request.method == 'POST':
        form = EnquiryForm(request.POST)
        if form.is_valid():
            enquiry = form.save(commit=False)
            enquiry.gym = gym
            enquiry.save()
            messages.success(request, 'Enquiry added successfully!')
            return redirect('enquiry_list')
    else:
        form = EnquiryForm()
    return render(request, 'enquiry/add_new_enquiry.html', {'form': form})
@login_required
def enquiry_list(request):
    gym = getattr(request, 'gym', None)
    enquiry_list = Enquiry.objects.filter(gym=gym)
    
    # Search functionality
    query = request.GET.get('q')
    if query:
        enquiry_list = enquiry_list.filter(
            Q(name__icontains=query) |
            Q(contact_number__icontains=query) |
            Q(email__icontains=query)
        ).distinct()

    # Pagination
    paginator = Paginator(enquiry_list, 10)  # Show 10 enquiries per page
    page_number = request.GET.get('page')
    enquiries = paginator.get_page(page_number)

    return render(request, 'enquiry/enquiry_list.html', {'enquiries': enquiries})
@login_required
def edit_enquiry(request, enquiry_id):
    gym = getattr(request, 'gym', None)
    enquiry = get_object_or_404(Enquiry, id=enquiry_id, gym=gym)
    if request.method == 'POST':
        form = EnquiryForm(request.POST, instance=enquiry)
        if form.is_valid():
            form.save()
            messages.success(request, 'Enquiry updated successfully!')
            return redirect('enquiry_list')
    else:
        form = EnquiryForm(instance=enquiry)
    return render(request, 'enquiry/edit_enquiry.html', {'form': form})
from django.http import JsonResponse
from django.views.decorators.http import require_POST

@login_required
@require_POST
def delete_enquiry(request, enquiry_id):
    gym = getattr(request, 'gym', None)
    enquiry = get_object_or_404(Enquiry, id=enquiry_id, gym=gym)
    try:
        enquiry.delete()
        messages.success(request, 'Enquiry has been deleted successfully.')
        return JsonResponse({'status': 'success', 'message': 'Enquiry deleted successfully.'})
    except Exception as e:
        messages.error(request, f'An error occurred: {e}')
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)