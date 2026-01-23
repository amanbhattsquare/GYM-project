from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from apps.superadmin.models import GymAdmin
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from .models import SubAdmin, ROLE_CHOICES
from apps.superadmin.models import Gym
from .models import SubAdminPermission


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

#gym login view
@never_cache
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

def add_gym_subadmin(request):
    if request.method == 'POST':
        # Personal Information
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        photo = request.FILES.get('photo')
        role = request.POST.get('role')

        # Login Credentials
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Permissions
        permissions = request.POST.getlist('permissions')

        try:
            # Create the user
            user = User.objects.create_user(username=username, email=email, password=password)
            if full_name:
                parts = full_name.split(' ', 1)
                user.first_name = parts[0]
                if len(parts) > 1:
                    user.last_name = parts[1]
            user.save()

            # Get the gym associated with the current admin
            gym_admin = GymAdmin.objects.get(user=request.user)
            gym = gym_admin.gym

            # Create the sub-admin profile
            sub_admin = SubAdmin.objects.create(
                user=user,
                gym=gym,
                phone_number=phone_number,
                address=address,
                photo=photo,
                role=role
            )

            # Assign permissions
            for perm_id in permissions:
                perm = Permission.objects.get(id=perm_id)
                SubAdminPermission.objects.create(sub_admin=sub_admin, permission_name=perm.codename)

            messages.success(request, 'Sub-admin created successfully!')
            return redirect('view_subadmins')

        except Exception as e:
            messages.error(request, f'Error creating sub-admin: {e}')
            # Fall through to render the form again with an error

    # Prepare the context for the template
    # This part will be more dynamic in a real application
    all_apps = ['dashboard', 'enquiry', 'members', 'trainers', 'attendance', 'billing', 'expenses', 'inventory', 'events', 'business_report', 'management', 'settings']
    app_permissions = {}
    for app in all_apps:
        content_type = ContentType.objects.filter(app_label=app).first()
        if content_type:
            perms = Permission.objects.filter(content_type=content_type)
            app_permissions[app] = perms

    context = {
        'app_permissions': app_permissions,
        'ROLE_CHOICES': ROLE_CHOICES
    }
    return render(request, 'login/add_gym_subadmin.html', context)


@login_required
def password_reset_page(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        user = request.user
        if not user.check_password(current_password):
            messages.error(request, 'Invalid current password.')
        elif new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
        elif ' ' in new_password:
            messages.error(request, 'Password cannot contain spaces.')
        else:
            user.set_password(new_password)
            user.save()
            
            # This part might need adjustment based on your models
            # Assuming a OneToOne or ForeignKey from User to GymAdmin
            if hasattr(user, 'gymadmin'):
                gym_admin = user.gymadmin
                if hasattr(gym_admin, 'gym'):
                    gym_admin.gym.password_reset_required = False
                    gym_admin.gym.save()
            
            messages.success(request, 'Password updated successfully.')
            return redirect('dashboard')
            
    return render(request, 'login/password_reset.html')

def view_subadmins(request):
    gym_admin = GymAdmin.objects.get(user=request.user)
    gym = gym_admin.gym
    sub_admins = SubAdmin.objects.filter(gym=gym)
    context = {
        'sub_admins': sub_admins
    }
    return render(request, 'login/view_subadmins.html', context)


def delete_subadmin(request, sub_admin_id):
    try:
        sub_admin = SubAdmin.objects.get(id=sub_admin_id)
        user = sub_admin.user
        sub_admin.delete()
        user.delete()
        messages.success(request, 'Sub-admin deleted successfully.')
    except SubAdmin.DoesNotExist:
        messages.error(request, 'Sub-admin not found.')
    except Exception as e:
        messages.error(request, f'An error occurred: {e}')
    return redirect('view_subadmins')

def edit_subadmin(request, sub_admin_id):
    try:
        sub_admin = SubAdmin.objects.get(id=sub_admin_id)
        user = sub_admin.user
    except SubAdmin.DoesNotExist:
        messages.error(request, 'Sub-admin not found.')
        return redirect('view_subadmins')

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        photo = request.FILES.get('photo')
        permissions = request.POST.getlist('permissions')
        role = request.POST.get('role')

        if full_name:
            parts = full_name.split(' ', 1)
            user.first_name = parts[0]
            if len(parts) > 1:
                user.last_name = parts[1]
        user.username = username
        user.email = email
        user.save()

        sub_admin.phone_number = phone_number
        sub_admin.address = address
        sub_admin.role = role
        if photo:
            sub_admin.photo = photo
        sub_admin.save()
        
        SubAdminPermission.objects.filter(sub_admin=sub_admin).delete()
        for perm_id in permissions:
            perm = Permission.objects.get(id=perm_id)
            SubAdminPermission.objects.create(sub_admin=sub_admin, permission_name=perm.codename)

        messages.success(request, 'Sub-admin updated successfully.')
        return redirect('view_subadmins')

    all_apps = ['dashboard', 'enquiry', 'members', 'trainers', 'attendance', 'billing', 'expenses', 'inventory', 'events', 'business_report', 'management', 'settings']
    app_permissions = {}
    for app in all_apps:
        content_type = ContentType.objects.filter(app_label=app).first()
        if content_type:
            perms = Permission.objects.filter(content_type=content_type)
            app_permissions[app] = perms
    
    assigned_permissions_qs = SubAdminPermission.objects.filter(sub_admin=sub_admin).values_list('permission_name', flat=True)
    assigned_permissions = list(Permission.objects.filter(codename__in=list(assigned_permissions_qs)).values_list('id', flat=True))

    context = {
        'sub_admin': sub_admin,
        'app_permissions': app_permissions,
        'assigned_permissions': list(assigned_permissions),
        'ROLE_CHOICES': ROLE_CHOICES
    }
    return render(request, 'login/add_gym_subadmin.html', context)