from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from apps.members.models import Member
from django.http import JsonResponse
from django.db.models.functions import TruncMonth
from django.db.models import Count
from apps.superadmin.models import GymAdmin

from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache

@never_cache
@login_required(login_url='login')
def dashboard(request):
    gym = getattr(request, 'gym', None)
    members = Member.objects.filter(gym=gym).prefetch_related('membership_history__plan').all()
    total_members = members.count()

    active_members = 0
    for member in members:
        if member.is_active:
            active_members += 1
    
    inactive_members = total_members - active_members
    
    # Calculate the date 30 days ago from the current date
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    
    # Count the number of members who joined in the last 30 days
    new_members_last_30_days = Member.objects.filter(gym=gym, membership_history__membership_start_date__gte=thirty_days_ago).distinct().count()

    context = {
        'total_members': total_members,
        'active_members': active_members,
        'inactive_members': inactive_members,
        'new_members_last_30_days': new_members_last_30_days,
    }
    return render(request, "dashboard.html", context)

def member_growth_chart_data(request):
    gym = getattr(request, 'gym', None)
    twelve_months_ago = timezone.now() - timedelta(days=365)
    
    member_growth = (
        Member.objects
        .filter(gym=gym, membership_history__membership_start_date__gte=twelve_months_ago)
        .annotate(month=TruncMonth('membership_history__membership_start_date'))
        .values('month')
        .annotate(count=Count('id', distinct=True))
        .order_by('month')
    )
    
    labels = [item['month'].strftime("%b %Y") for item in member_growth]
    data = [item['count'] for item in member_growth]
    
    return JsonResponse({'labels': labels, 'data': data})

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
    return redirect('login')