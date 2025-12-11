from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from apps.superadmin.models import GymAdmin
from django.views.decorators.cache import never_cache


@never_cache
def superadmin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_superuser:
            login(request, user)
            request.session['role'] = 'superadmin'
            return redirect('superadmin:dashboard')
        else:
            messages.error(request, 'Invalid username or password for superadmin.')
    return render(request, 'login/superadmin_login.html')


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_superuser:
                request.session['role'] = 'superadmin'
                # Redirect to a superadmin-specific dashboard if you have one
                return redirect('dashboard') 
            
            try:
                gym_admin = GymAdmin.objects.get(user=user)
                request.session['gym_id'] = gym_admin.gym.id
                request.session['role'] = 'gym_admin'
                return redirect('dashboard')
            except GymAdmin.DoesNotExist:
                # Handle regular users or other roles if necessary
                pass

            messages.error(request, 'Invalid user role.')
            return redirect('login')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login/login.html')


def user_logout(request):
    if 'gym_id' in request.session:
        del request.session['gym_id']
    if 'role' in request.session:
        del request.session['role']
    logout(request)
    return redirect('index')