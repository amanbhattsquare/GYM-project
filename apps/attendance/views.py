from django.shortcuts import render, redirect
from django.utils import timezone
from apps.members.models import Member
from apps.trainers.models import Trainer
from .models import MemberAttendance, TrainerAttendance

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


def member_attendance(request):
    today = timezone.now().date()
    if request.method == 'POST':
        member_ids = request.POST.getlist('member_ids')
        for member_id in member_ids:
            status = request.POST.get(f'status_{member_id}') == 'present'
            MemberAttendance.objects.update_or_create(
                member_id=member_id,
                date=today,
                defaults={'status': status}
            )
        return redirect('member_attendance')

    members = Member.objects.all()
    attendance_records = MemberAttendance.objects.filter(date=today)
    attendance_status = {record.member_id: record.status for record in attendance_records}

    member_list = []
    for member in members:
        member_list.append({
            'id': member.id,
            'name': f'{member.first_name} {member.last_name}',
            'status': attendance_status.get(member.id, False)
        })

    return render(request, 'attendance/member_attendance.html', {'members': member_list, 'date': today})