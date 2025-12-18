from django.shortcuts import render, redirect, get_object_or_404
from .models import Event
from django.contrib.auth.decorators import login_required
import csv
from django.http import HttpResponse
from django.contrib import messages

@login_required
def event_list(request):
    events = Event.objects.all()
    return render(request, 'events/event_list.html', {'events': events})

@login_required
def create_event(request):
    if request.method == 'POST':
        event_name = request.POST.get('event_name')
        event_type = request.POST.get('event_type')
        description = request.POST.get('description')
        banner_image = request.FILES.get('banner_image')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        trainer_name = request.POST.get('trainer_name')
        location = request.POST.get('location')
        max_participants = request.POST.get('max_participants')
        registration_deadline = request.POST.get('registration_deadline')
        fee = request.POST.get('fee')
        status = request.POST.get('status')

        Event.objects.create(
            event_name=event_name,
            event_type=event_type,
            description=description,
            banner_image=banner_image,
            start_date=start_date,
            end_date=end_date,
            trainer_name=trainer_name,
            location=location,
            max_participants=max_participants,
            registration_deadline=registration_deadline,
            fee=fee,
            status=status,
        )
        return redirect('events:event_list')

    event_types = Event.EventType.choices
    locations = Event.EventLocation.choices
    fees = Event.EventFee.choices
    statuses = Event.EventStatus.choices

    context = {
        'event_types': event_types,
        'locations': locations,
        'fees': fees,
        'statuses': statuses,
    }
    return render(request, 'events/create_event.html', context)

@login_required
def edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        event.event_name = request.POST.get('event_name')
        event.event_type = request.POST.get('event_type')
        event.description = request.POST.get('description')
        if request.FILES.get('banner_image'):
            event.banner_image = request.FILES.get('banner_image')
        event.start_date = request.POST.get('start_date')
        event.end_date = request.POST.get('end_date')
        event.trainer_name = request.POST.get('trainer_name')
        event.location = request.POST.get('location')
        event.max_participants = request.POST.get('max_participants')
        event.registration_deadline = request.POST.get('registration_deadline')
        event.fee = request.POST.get('fee')
        event.status = request.POST.get('status')
        event.save()
        return redirect('events:event_list')

    event_types = Event.EventType.choices
    locations = Event.EventLocation.choices
    fees = Event.EventFee.choices
    statuses = Event.EventStatus.choices

    context = {
        'event': event,
        'event_types': event_types,
        'locations': locations,
        'fees': fees,
        'statuses': statuses,
    }
    return render(request, 'events/edit_event.html', context)

@login_required
def cancel_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    event.delete()
    return redirect('events:event_list')

@login_required
def duplicate_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    event.pk = None
    event.event_name = f"{event.event_name} (Copy)"
    event.save()
    return redirect('events:event_list')

@login_required
def export_attendees(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{event.event_name}_attendees.csv"'

    writer = csv.writer(response)
    writer.writerow(['Member ID', 'Name', 'Email', 'Mobile Number'])

    for member in event.registered_members.all():
        writer.writerow([member.member_id, member.name, member.email, member.mobile_number])

    return response

@login_required
def notify_members(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    # Placeholder for sending notifications
    messages.success(request, f"Notifications for {event.event_name} will be sent to all registered members.")
    return redirect('events:event_list')