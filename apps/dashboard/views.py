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
from django.db import models

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

    # Upcoming and Expired Members
    today = timezone.now().date()
    seven_days_from_now = today + timedelta(days=7)

    upcoming_expiries = []
    expired_members = []

    for member in members:
        latest_membership = member.latest_membership
        if latest_membership:
            end_date = latest_membership.get_end_date()
            if end_date:
                if today <= end_date <= seven_days_from_now:
                    upcoming_expiries.append(member)
                elif end_date < today:
                    expired_members.append(member)

    # Sort and limit the lists
    upcoming_expiries = sorted(upcoming_expiries, key=lambda m: m.latest_membership.get_end_date())[:10]
    expired_members = sorted(expired_members, key=lambda m: m.latest_membership.get_end_date(), reverse=True)[:10]

    context = {
        'total_members': total_members,
        'active_members': active_members,
        'inactive_members': inactive_members,
        'new_members_last_30_days': new_members_last_30_days,
        'upcoming_expiries': upcoming_expiries,
        'expired_members': expired_members,
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