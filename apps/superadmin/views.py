from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import User
from .forms import GymForm, GymAdminForm
from .models import Gym, GymAdmin

def add_gym(request):
    if request.method == 'POST':
        form = GymForm(request.POST, request.FILES)
        if form.is_valid():
            # Don't save the form to the database yet
            gym = form.save(commit=False)
            # Create a new user for the gym
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = User.objects.create_user(username=username, password=password)
            user.save()
            # Now save the gym to the database
            gym.save()
            return redirect('superadmin:gym_list')
    else:
        form = GymForm()
    return render(request, 'superadmin/add_gym.html', {'form': form})

def gym_list(request):
    gyms_list = Gym.objects.all()
    for gym in gyms_list:
        gym.has_admin = GymAdmin.objects.filter(gym=gym).exists()

    page = request.GET.get('page', 1)

    paginator = Paginator(gyms_list, 10)  # Show 10 gyms per page

    try:
        gyms = paginator.page(page)
    except PageNotAnInteger:
        gyms = paginator.page(1)
    except EmptyPage:
        gyms = paginator.page(paginator.num_pages)

    return render(request, 'superadmin/gym_list.html', {'gyms': gyms})

def update_gym(request, gym_id):
    gym = get_object_or_404(Gym, pk=gym_id)
    if request.method == 'POST':
        form = GymForm(request.POST, request.FILES, instance=gym)
        if form.is_valid():
            form.save()
            return redirect('superadmin:gym_list')
    else:
        form = GymForm(instance=gym)
    return render(request, 'superadmin/add_gym.html', {'form': form})

def delete_gym(request, gym_id):
    gym = get_object_or_404(Gym, pk=gym_id)
    gym.delete()
    return redirect('superadmin:gym_list')

def create_gym_admin(request, gym_id):
    gym = get_object_or_404(Gym, pk=gym_id)
    if request.method == 'POST':
        form = GymAdminForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = User.objects.create_user(username=username, password=password)
            GymAdmin.objects.create(user=user, gym=gym)
            return redirect('superadmin:gym_list')
    else:
        form = GymAdminForm()
    return render(request, 'superadmin/create_gym_admin.html', {'form': form, 'gym': gym})