from django.contrib import admin
from .models import BEMMember, Event, NPM_Whitelist

@admin.register(BEMMember)
class BEMMemberAdmin(admin.ModelAdmin):
    list_display = ['sso_account', 'role', 'img_url']
    list_filter = ['role']
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change:  # If the object is being created
            if obj.npm:
                NPM_Whitelist.objects.create(npm=obj.npm)

    def delete_model(self, request, obj):
        if obj.npm:
            obj.npm.delete()
        super().delete_model(request, obj)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['start', 'end']