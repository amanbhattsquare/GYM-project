from django.contrib import admin
from .models import Gym, Subscription

@admin.register(Gym)
class GymAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'is_active', 'created_at')
    search_fields = ('name', 'email')
    list_filter = ('is_active',)

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('gym', 'plan', 'start_date', 'end_date', 'is_active')
    search_fields = ('gym__name', 'plan')
    list_filter = ('is_active', 'plan')