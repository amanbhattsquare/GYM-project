from django.shortcuts import render, redirect
from django.utils import timezone
from apps.members.models import Member
from apps.trainers.models import Trainer
from .models import MemberAttendance, TrainerAttendance
from django.core.paginator import Paginator
from django.db.models import Q

def trainer_attendance(request):
    today = timezone.now().date()
    if request.method == 'POST':
        trainer_ids = request.POST.getlist('trainer_ids')
        for trainer_id in trainer_ids:
            status = request.POST.get(f'status_{trainer_id}') == 'present'
            TrainerAttendance.objects.update_or_create(
                trainer_id=trainer_id,
                date=today,
                defaults={'status': status}
            )
        return redirect('trainer_attendance')

    trainers = Trainer.objects.all()
    attendance_records = TrainerAttendance.objects.filter(date=today)
    attendance_status = {record.trainer_id: record.status for record in attendance_records}

    trainer_list = []
    for trainer in trainers:
        trainer_list.append({
            'id': trainer.id,
            'name': trainer.name,
            'status': attendance_status.get(trainer.id, False)
        })

    return render(request, 'attendance/trainer_attendance.html', {'trainers': trainer_list, 'date': today})

def attendance_report(request):
    member_attendance = MemberAttendance.objects.all().order_by('-date')
    trainer_attendance = TrainerAttendance.objects.all().order_by('-date')
    return render(request, 'attendance/attendance_report.html', {
        'member_attendance': member_attendance,
        'trainer_attendance': trainer_attendance
    })

from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Value
from django.db.models.functions import Concat
from apps.members.models import Member
from .models import MemberAttendance, TrainerAttendance
from apps.trainers.models import Trainer

def member_attendance(request):
    today = timezone.now().date()

    if request.method == 'POST':
        action = request.POST.get('action')
        member_id = request.POST.get('member_id')
        quick_checkin_id = request.POST.get('quick_checkin_id')

        if quick_checkin_id:
            try:
                member = Member.objects.get(membership_id=quick_checkin_id, status='active')
                MemberAttendance.objects.create(member=member, check_in_time=timezone.now())
                messages.success(request, f'{member.name} checked in successfully.')
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
            Q(membership_id__icontains=query)
        ).order_by('first_name', 'last_name')
    else:
        members_list = Member.objects.all().order_by('first_name', 'last_name')

    paginator = Paginator(members_list, 10)
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
            'records': records,
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