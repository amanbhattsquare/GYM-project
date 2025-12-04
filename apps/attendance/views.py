from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Value
from django.db.models.functions import Concat
from apps.members.models import Member
from .models import MemberAttendance, TrainerAttendance
from apps.trainers.models import Trainer
from datetime import datetime, timedelta
from django.conf import settings
from django.core.serializers import serialize
import json


def trainer_attendance(request):
    today = timezone.now().date()

    if request.method == 'POST':
        action = request.POST.get('action')
        trainer_id = request.POST.get('trainer_id')
        quick_checkin_id = request.POST.get('quick_checkin_id')

        if quick_checkin_id:
            try:
                trainer = Trainer.objects.get(trainer_id=quick_checkin_id, is_active=True)
                TrainerAttendance.objects.create(trainer=trainer, check_in_time=timezone.now())
                messages.success(request, f'{trainer.name} checked in successfully.')
            except Trainer.DoesNotExist:
                messages.error(request, 'Invalid or inactive Trainer ID.')
            return redirect('trainer_attendance')

        if trainer_id and action:
            trainer = get_object_or_404(Trainer, id=trainer_id)
            if action == 'checkin':
                TrainerAttendance.objects.create(trainer=trainer, check_in_time=timezone.now())
                messages.success(request, f'{trainer.name} checked in successfully.')
            elif action == 'checkout':
                attendance_record = TrainerAttendance.objects.filter(trainer=trainer, check_in_time__date=today, check_out_time__isnull=True).first()
                if attendance_record:
                    attendance_record.check_out_time = timezone.now()
                    attendance_record.status = 'outside'
                    attendance_record.save()
                    messages.success(request, f'{trainer.name} checked out successfully.')
                else:
                    messages.error(request, 'Trainer is not checked in.')
            return redirect('trainer_attendance')

    # Stats
    checked_in_today = TrainerAttendance.objects.filter(check_in_time__date=today).values('trainer').distinct().count()
    currently_inside = TrainerAttendance.objects.filter(status='inside', check_in_time__date=today).count()
    total_trainers = Trainer.objects.count()

    # Get all active trainers
    query = request.GET.get('q')
    if query:
        trainers_list = Trainer.objects.filter(
            Q(name__icontains=query) |
            Q(mobile__icontains=query)
        ).order_by('name')
    else:
        trainers_list = Trainer.objects.all().order_by('name')

    paginator = Paginator(trainers_list, settings.ITEMS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get today's attendance records for the current page of trainers
    trainer_ids_on_page = [trainer.id for trainer in page_obj]
    attendance_today = TrainerAttendance.objects.filter(
        trainer_id__in=trainer_ids_on_page, 
        check_in_time__date=today
    ).order_by('-check_in_time')

    # Create a dictionary for quick lookup
    attendance_dict = {}
    for record in attendance_today:
        if record.trainer_id not in attendance_dict:
            attendance_dict[record.trainer_id] = []
        attendance_dict[record.trainer_id].append(record)

    # Combine trainer data with attendance status
    trainer_data = []
    for trainer in page_obj:
        records = attendance_dict.get(trainer.id, [])
        latest_record = records[0] if records else None
        trainer_data.append({
            'trainer': trainer,
            'records': sorted(records, key=lambda x: x.check_in_time, reverse=True) if records else [],
            'is_checked_in': latest_record and latest_record.status == 'inside'
        })

    context = {
        'today': today,
        'trainer_data': trainer_data,
        'page_obj': page_obj,
        'checked_in_today': checked_in_today,
        'currently_inside': currently_inside,
        'total_trainers': total_trainers,
    }
    return render(request, 'attendance/trainer_attendance.html', context)

def member_attendance(request):
    today = timezone.now().date()

    if request.method == 'POST':
        action = request.POST.get('action')
        member_id = request.POST.get('member_id')
        quick_checkin_id = request.POST.get('quick_checkin_id')

        if quick_checkin_id and action:
            try:
                member = get_object_or_404(Member, member_id=quick_checkin_id, status='active')
                if action == 'checkin':
                    MemberAttendance.objects.create(member=member, check_in_time=timezone.now())
                    messages.success(request, f'{member.name} checked in successfully.')
                elif action == 'checkout':
                    attendance_record = MemberAttendance.objects.filter(member=member, check_in_time__date=today, check_out_time__isnull=True).first()
                    if attendance_record:
                        attendance_record.check_out_time = timezone.now()
                        attendance_record.status = 'outside'
                        attendance_record.save()
                        messages.success(request, f'{member.name} checked out successfully.')
                    else:
                        messages.error(request, 'Member is not checked in.')
            except Member.DoesNotExist:
                messages.error(request, 'Invalid or inactive Membership ID.')
            return redirect('member_attendance')

        if member_id and action:
            member = get_object_or_404(Member, id=member_id)
            if action == 'checkin':
                MemberAttendance.objects.create(member=member, check_in_time=timezone.now())
                messages.success(request, f'{member.name} checked in successfully.')
            elif action == 'checkout':
                attendance_record = MemberAttendance.objects.filter(member=member, check_in_time__date=today, check_out_time__isnull=True).first()
                if attendance_record:
                    attendance_record.check_out_time = timezone.now()
                    attendance_record.status = 'outside'
                    attendance_record.save()
                    messages.success(request, f'{member.name} checked out successfully.')
                else:
                    messages.error(request, 'Member is not checked in.')
            return redirect('member_attendance')

    # Stats
    checked_in_today = MemberAttendance.objects.filter(check_in_time__date=today).values('member').distinct().count()
    currently_inside = MemberAttendance.objects.filter(status='inside', check_in_time__date=today).count()
    total_members = Member.objects.count()

    # Get all active members
    query = request.GET.get('q')
    if query:
        members_list = Member.objects.annotate(full_name=Concat('first_name', Value(' '), 'last_name')).filter(
            Q(full_name__icontains=query) |
            Q(mobile_number__icontains=query) |
            Q(member_id__icontains=query)
        ).order_by('first_name', 'last_name')
    else:
        members_list = Member.objects.all().order_by('first_name', 'last_name')

    paginator = Paginator(members_list, settings.ITEMS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get today's attendance records for the current page of members
    member_ids_on_page = [member.id for member in page_obj]
    attendance_today = MemberAttendance.objects.filter(
        member_id__in=member_ids_on_page, 
        check_in_time__date=today
    ).order_by('-check_in_time')

    # Create a dictionary for quick lookup
    attendance_dict = {}
    for record in attendance_today:
        if record.member_id not in attendance_dict:
            attendance_dict[record.member_id] = []
        attendance_dict[record.member_id].append(record)

    # Combine member data with attendance status
    member_data = []
    for member in page_obj:
        records = attendance_dict.get(member.id, [])
        latest_record = records[0] if records else None
        member_data.append({
            'member': member,
            'records': sorted(records, key=lambda x: x.check_in_time, reverse=True) if records else [],
            'is_checked_in': latest_record and latest_record.status == 'inside'
        })

    context = {
        'today': today,
        'member_data': member_data,
        'page_obj': page_obj,
        'checked_in_today': checked_in_today,
        'currently_inside': currently_inside,
        'total_members': total_members,
    }
    return render(request, 'attendance/member_attendance.html', context)

import json
from django.core.serializers import serialize

def attendance_report(request):
    user_type = request.GET.get('user_type', 'member')
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    user_id = request.GET.get('user_id')

    # Default to today if no dates are provided
    today = timezone.now().date()
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else today
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else today
    
    records = None
    if user_type == 'member':
        records = MemberAttendance.objects.filter(
            check_in_time__date__range=[start_date, end_date]
        ).select_related('member').order_by('-check_in_time')
        if user_id:
            records = records.filter(member__id=user_id)
    else: # trainer
        records = TrainerAttendance.objects.filter(
            check_in_time__date__range=[start_date, end_date]
        ).select_related('trainer').order_by('-check_in_time')
        if user_id:
            records = records.filter(trainer__id=user_id)

    all_members = Member.objects.all()
    all_trainers = Trainer.objects.all()

    paginator = Paginator(records, settings.ITEMS_PER_PAGE) # 15 records per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'records': page_obj,
        'page_obj': page_obj,
        'user_type': user_type,
        'start_date': start_date,
        'end_date': end_date,
        'members': serialize('json', all_members),
        'trainers': serialize('json', all_trainers),
        'selected_user_id': int(user_id) if user_id else None,
    }
    return render(request, 'attendance/attendance_report.html', context)