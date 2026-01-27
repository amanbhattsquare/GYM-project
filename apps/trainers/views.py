from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse

from .models import Trainer
from .forms import TrainerForm

from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.db import IntegrityError



@never_cache
@login_required(login_url='login')
def trainer_list(request):
    gym = getattr(request, 'gym', None)
    trainers_list = Trainer.objects.filter(gym=gym)

    query = request.GET.get('q')
    if query:
        trainers_list = trainers_list.filter(
            Q(name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone__icontains=query) |
            Q(specialization__icontains=query)
        ).distinct()

    paginator = Paginator(trainers_list, 10)  # Show 10 trainers per page
    page = request.GET.get('page')

    try:
        trainers = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        trainers = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        trainers = paginator.page(paginator.num_pages)

    return render(request, 'trainers/trainer_list.html', {'trainers': trainers})
    
@never_cache
@login_required(login_url='login')
def add_trainer(request):
    gym = getattr(request, 'gym', None)
    if request.method == 'POST':
        form = TrainerForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                trainer = form.save(commit=False)
                trainer.gym = gym
                trainer.save()
                messages.success(request, 'Trainer added successfully!')
                return redirect('trainer_list')
            except IntegrityError:
                form.add_error('email', 'A trainer with this email already exists.')
    else:
        form = TrainerForm()
    return render(request, 'trainers/add_trainer.html', {'form': form})

@never_cache
@login_required(login_url='login')
def edit_trainer(request, trainer_id):
    gym = getattr(request, 'gym', None)
    trainer = get_object_or_404(Trainer, id=trainer_id, gym=gym)
    if request.method == 'POST':
        form = TrainerForm(request.POST, request.FILES, instance=trainer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Trainer updated successfully!')
            return redirect('trainer_list')
    else:
        form = TrainerForm(instance=trainer)
    return render(request, 'trainers/edit_trainer.html', {'form': form})

from django.views.decorators.http import require_POST

@never_cache
@login_required(login_url='login')
@require_POST
def delete_trainer(request, trainer_id):
    gym = getattr(request, 'gym', None)
    trainer = get_object_or_404(Trainer, id=trainer_id, gym=gym)
    try:
        trainer.delete()
        messages.success(request, 'Trainer has been deleted successfully.')
        return JsonResponse({'status': 'success', 'message': 'Trainer deleted successfully.'})
    except Exception as e:
        messages.error(request, f'An error occurred: {e}')
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@never_cache
@login_required(login_url='login')
def toggle_trainer_status(request, trainer_id):
    gym = getattr(request, 'gym', None)
    trainer = get_object_or_404(Trainer, id=trainer_id, gym=gym)
    trainer.is_active = not trainer.is_active
    trainer.save()
    messages.success(request, f"Trainer {trainer.name} has been marked as {'Active' if trainer.is_active else 'Inactive'}.")
    return redirect('trainer_list')