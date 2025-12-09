from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import User
from .forms import GymForm, GymAdminForm
from .models import Gym, GymAdmin
from apps.members.models import Member, MembershipHistory

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
        gym_admin = GymAdmin.objects.filter(gym=gym).first()
        if gym_admin and gym_admin.user:
            gym.admin_name = f"{gym_admin.user.first_name} {gym_admin.user.last_name}"
            gym.admin_username = gym_admin.user.username
        else:
            gym.admin_name = "N/A"
            gym.admin_username = "N/A"

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

def gym_profile(request, gym_id):
    gym = get_object_or_404(Gym, pk=gym_id)
    form = GymForm(instance=gym)
    members = Member.objects.filter(gym=gym)
    membership_history = MembershipHistory.objects.filter(gym=gym).order_by('-created_at')
    gym_admin = GymAdmin.objects.filter(gym=gym).first()
    admin_form = GymAdminForm()
    return render(request, 'superadmin/gym_profile.html', {
        'gym': gym, 
        'form': form, 
        'members': members, 
        'membership_history': membership_history,
        'gym_admin': gym_admin,
        'admin_form': admin_form
    })

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