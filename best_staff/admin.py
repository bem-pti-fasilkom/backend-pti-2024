from django.contrib import admin
from django import forms
from .models import *

class BEMMemberForm(forms.ModelForm):
    class Meta:
        model = BEMMember
        fields = ['sso_account', 'role', 'img_url', 'npm'] 
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if instance.npm:
            instance.birdept = instance.npm.birdept
        if commit:
            instance.save()
        return instance

@admin.register(BEMMember)
class BEMMemberAdmin(admin.ModelAdmin):
    form = BEMMemberForm
    list_display = ['sso_account', 'role', 'img_url', 'npm', 'birdept']
    list_filter = ['role', 'birdept']
    search_fields = ['sso_account__username', 'npm__npm']
    autocomplete_fields = ['npm']  
    readonly_fields = ['birdept']  

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['start', 'end']

@admin.register(Birdept)
class BirdeptAdmin(admin.ModelAdmin):
    list_display = ['nama', 'desc']
    search_fields = ['nama']
    
    def get_readonly_fields(self, request, obj=None):
        if obj: 
            return ['galeri']
        return []

@admin.register(NPM_Whitelist)
class NPMWhitelistAdmin(admin.ModelAdmin):
    list_display = ['npm', 'birdept']
    list_filter = ['birdept']
    search_fields = ['npm']
    autocomplete_fields = ['birdept']