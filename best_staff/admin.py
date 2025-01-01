from django.contrib import admin
from .models import BEMMember, Event

@admin.register(BEMMember)
class BEMMemberAdmin(admin.ModelAdmin):
    list_display = ['sso_account', 'role', 'img_url']
    list_filter = ['role']

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['start', 'end']