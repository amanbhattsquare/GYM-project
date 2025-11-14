from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .models import Trainer
from .forms import TrainerForm

def trainer_list(request):
    trainers = Trainer.objects.all()
    return render(request, 'trainers/trainer_list.html', {'trainers': trainers})

def add_trainer(request):
    if request.method == 'POST':
        form = TrainerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Trainer added successfully!')
            return redirect('trainer_list')
    else:
        form = TrainerForm()
    return render(request, 'trainers/add_trainer.html', {'form': form})

def edit_trainer(request, trainer_id):
    trainer = get_object_or_404(Trainer, id=trainer_id)
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

@require_POST
def delete_trainer(request, trainer_id):
    trainer = get_object_or_404(Trainer, id=trainer_id)
    trainer.delete()
    messages.success(request, 'Trainer deleted successfully!')
    return redirect('trainer_list')