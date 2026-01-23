from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from apps.members.models import Member, MembershipHistory
from django.http import JsonResponse
from django.db.models.functions import TruncMonth
from django.db.models import Count
from apps.superadmin.models import GymAdmin
from django.db import models
from apps.trainers.models import Trainer
from apps.attendance.models import MemberAttendance, TrainerAttendance
from apps.enquiry.models import Enquiry
from apps.billing.models import Payment


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

    # Member growth data for chart
    six_months_ago = timezone.now() - timedelta(days=180)
    
    # New members per month
    new_members_data = Member.objects.filter(
        gym=gym,
        membership_history__membership_start_date__gte=six_months_ago
    ).annotate(
        month=TruncMonth('membership_history__membership_start_date')
    ).values('month').annotate(
        count=Count('id', distinct=True)
    ).order_by('month')

    # Active members per month
    active_members_data = []
    for i in range(6):
        month_start = (timezone.now() - timedelta(days=i*30)).replace(day=1).date()
        
        active_count = 0
        for member in members:
            latest_membership = member.latest_membership
            if latest_membership:
                end_date = latest_membership.get_end_date()
                if end_date and latest_membership.membership_start_date < month_start and end_date >= month_start:
                    active_count += 1
        
        active_members_data.append({
            'month': month_start,
            'count': active_count
        })
    active_members_data.reverse()

    month_labels = [item['month'].strftime("%b") for item in new_members_data]
    new_member_counts = [item['count'] for item in new_members_data]
    active_member_counts = [item['count'] for item in active_members_data]
    
    # Attendance data
    today_min = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_max = timezone.now().replace(hour=23, minute=59, second=59, microsecond=999999)
    
    member_attendance = MemberAttendance.objects.filter(gym=gym, check_in_time__range=(today_min, today_max))
    trainer_attendance = TrainerAttendance.objects.filter(gym=gym, check_in_time__range=(today_min, today_max))
    
    today_attendance_count = member_attendance.count() + trainer_attendance.count()
    
    # Combine and sort attendance
    combined_attendance = sorted(
        list(member_attendance) + list(trainer_attendance),
        key=lambda x: x.check_in_time,
        reverse=True
    )[:10]
    
    # Attendance overview
    present_members_count = member_attendance.count()
    present_trainers_count = trainer_attendance.count()
    
    total_trainers = Trainer.objects.filter(gym=gym).count()
    
    absent_members_count = total_members - present_members_count
    if absent_members_count < 0:
        absent_members_count = 0

    absent_trainers_count = total_trainers - present_trainers_count
    if absent_trainers_count < 0:
        absent_trainers_count = 0

    # Enquiries
    recent_enquiries = Enquiry.objects.filter(gym=gym).order_by('-enquiry_date')[:5]
    total_enquiries = Enquiry.objects.filter(gym=gym).count()

    # Dues
    dues = MembershipHistory.objects.filter(gym=gym, paid_amount__lt=models.F('total_amount')).order_by('-membership_start_date')
    total_dues = dues.count()
    recent_dues = dues[:5]

    # Recent Payments
    recent_payments = Payment.objects.filter(member__gym=gym).order_by('-payment_date')[:10]
    total_recent_payments = sum(payment.amount for payment in recent_payments)

    # Birthday's
    today = timezone.now().date()
    today_birthdays = Member.objects.filter(gym=gym, date_of_birth__month=today.month, date_of_birth__day=today.day)
    
    # Upcoming Birthdays (next 7 days)
    upcoming_birthdays_list = []
    for i in range(1, 8):
        future_date = today + timedelta(days=i)
        birthdays_on_date = Member.objects.filter(gym=gym, date_of_birth__month=future_date.month, date_of_birth__day=future_date.day)
        for member in birthdays_on_date:
            upcoming_birthdays_list.append(member)


    context = {
        'total_members': total_members,
        'active_members': active_members,
        'inactive_members': inactive_members,
        'new_members_last_30_days': new_members_last_30_days,
        'upcoming_expiries': upcoming_expiries,
        'expired_members': expired_members,
        'month_labels': month_labels,
        'new_member_counts': new_member_counts,
        'active_member_counts': active_member_counts,
        'today_attendance_count': today_attendance_count,
        'todays_attendance': combined_attendance,
        'present_members_count': present_members_count,
        'present_trainers_count': present_trainers_count,
        'absent_members_count': absent_members_count,
        'absent_trainers_count': absent_trainers_count,
        'recent_enquiries': recent_enquiries,
        'total_enquiries': total_enquiries,
        'recent_dues': recent_dues,
        'total_dues': total_dues,
        'recent_payments': recent_payments,
        'total_recent_payments': total_recent_payments,
        'today_birthdays': today_birthdays,
        'upcoming_birthdays': upcoming_birthdays_list,
    }
    return render(request, "dashboard.html", context)


def member_growth_chart_data(request):
    gym = getattr(request, 'gym', None)
    six_months_ago = timezone.now() - timedelta(days=180)
    
    # New members per month
    new_members_data = Member.objects.filter(
        gym=gym,
        membership_history__membership_start_date__gte=six_months_ago
    ).annotate(
        month=TruncMonth('membership_history__membership_start_date')
    ).values('month').annotate(
        count=Count('id', distinct=True)
    ).order_by('month')

    # Active members per month
    active_members_data = []
    for i in range(6):
        month_start = (timezone.now() - timedelta(days=i*30)).replace(day=1).date()
        
        active_count = 0
        for member in Member.objects.filter(gym=gym):
            latest_membership = member.latest_membership
            if latest_membership:
                end_date = latest_membership.get_end_date()
                if end_date and latest_membership.membership_start_date < month_start and end_date >= month_start:
                    active_count += 1
        
        active_members_data.append({
            'month': month_start,
            'count': active_count
        })
    active_members_data.reverse()

    labels = [item['month'].strftime("%b") for item in new_members_data]
    new_members = [item['count'] for item in new_members_data]
    active_members = [item['count'] for item in active_members_data]
    
    return JsonResponse({
        'labels': labels,
        'new_members': new_members,
        'active_members': active_members
    })