from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Event(models.Model):
    class EventType(models.TextChoices):
        WORKOUT = 'Workout', _('Workout')
        SEMINAR = 'Seminar', _('Seminar')
        COMPETITION = 'Competition', _('Competition')
        OFFER = 'Offer', _('Offer')

    class EventStatus(models.TextChoices):
        UPCOMING = 'Upcoming', _('Upcoming')
        ONGOING = 'Ongoing', _('Ongoing')
        COMPLETED = 'Completed', _('Completed')
        DRAFT = 'Draft', _('Draft')
        PUBLISHED = 'Published', _('Published')

    class EventLocation(models.TextChoices):
        GYM = 'Gym', _('Gym')
        ONLINE = 'Online', _('Online')

    class EventFee(models.TextChoices):
        FREE = 'Free', _('Free')
        PAID = 'Paid', _('Paid')

    event_name = models.CharField(max_length=255)
    event_type = models.CharField(
        max_length=20, choices=EventType.choices, default=EventType.WORKOUT)
    event_category = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    banner_image = models.ImageField(
        upload_to='event_banners/', null=True, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    trainer_name = models.CharField(max_length=100, null=True, blank=True)
    location = models.CharField(
        max_length=10, choices=EventLocation.choices, default=EventLocation.GYM)
    max_participants = models.PositiveIntegerField()
    registration_deadline = models.DateTimeField()
    fee = models.CharField(max_length=10, choices=EventFee.choices, default=EventFee.FREE)
    status = models.CharField(
        max_length=20, choices=EventStatus.choices, default=EventStatus.UPCOMING)
    registered_members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='registered_events', blank=True)

    def __str__(self):
        return self.event_name