from django.contrib import admin
from django import forms
from .models import BEMMember, Event, Birdept, Vote, Winner
from .serializers import SSOAccountSerializer
from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .serializers import SSOAccountSerializer
from backend_pti.settings import DEBUG
        
if DEBUG:
    @admin.register(Vote)
    class VoteAdmin(admin.ModelAdmin):
        list_display = ['voter', 'voted', 'created_at']
        list_filter = ['voter', 'voted']
        search_fields = ['voter', 'voted']
        readonly_fields = ['created_at']
        
        def get_readonly_fields(self, request, obj=None):
            if obj:
                return ['voter', 'voted', 'created_at']
            return ['created_at']
        
        def get_fields(self, request, obj=None):
            fields = list(super().get_fields(request, obj))
            if 'created_at' not in fields:
                fields.append('created_at')
            return fields

@admin.register(BEMMember)
class BEMMemberAdmin(admin.ModelAdmin):
    list_display = ['sso_account', 'role', 'img_url', 'get_birdept']
    list_filter = ['role', 'birdept']
    search_fields = ['sso_account__username'] 

    def get_birdept(self, obj):
        return [birdept.nama for birdept in obj.birdept.all()]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.npm = obj.sso_account.npm
        obj.save()

    # def get_fields(self, request, obj=None):
    #     fields = list(super().get_fields(request, obj))
    #     if 'npm' not in fields:
    #         fields.extend(['npm', 'birdept'])
    #     return fields 

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['start', 'end']

@admin.register(Birdept)
class BirdeptAdmin(admin.ModelAdmin):
    list_display = ['nama', 'deskripsi']
    search_fields = ['nama']
    
    def get_readonly_fields(self, request, obj=None):
        if obj: 
            return ['galeri']
        return []
    
@admin.register(Winner)
class WinnerAdmin(admin.ModelAdmin):
    list_display = ["member", "pesan_singkat", "month", "year", "rank"]
    list_filter = ["month", "year"]
    search_fields = ["member"]