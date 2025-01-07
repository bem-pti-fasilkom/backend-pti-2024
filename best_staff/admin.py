from django.contrib import admin
from django import forms
from .models import *
from .serializers import SSOAccountSerializer

from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import *
from .serializers import SSOAccountSerializer

class BEMMemberForm(forms.ModelForm):
    class Meta:
        model = BEMMember
        fields = ['sso_account', 'role', 'img_url']
        
    def clean(self):
        cleaned_data = super().clean()
        sso_account = cleaned_data.get('sso_account')
        
        if sso_account:
            serializer = SSOAccountSerializer(sso_account)
            npm_value = serializer.data.get('npm')
            
            try:
                whitelist = NPM_Whitelist.objects.filter(npm=npm_value).first()
                
                if not whitelist:
                    raise forms.ValidationError(_('NPM tidak terdaftar dalam whitelist'))
                
                self.whitelist = whitelist
            except:
                raise forms.ValidationError(_('Error'))
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.npm = self.whitelist
        instance.birdept = self.whitelist.birdept
        
        if commit:
            instance.save()
        
        return instance
        
@admin.register(BEMMember)
class BEMMemberAdmin(admin.ModelAdmin):
    form = BEMMemberForm
    list_display = ['sso_account', 'role', 'img_url', 'npm', 'birdept']
    list_filter = ['role', 'birdept']
    search_fields = ['sso_account__username'] 
    readonly_fields = ['npm', 'birdept']  
    
    def get_fields(self, request, obj=None):
        fields = list(super().get_fields(request, obj))
        if 'npm' not in fields:
            fields.extend(['npm', 'birdept'])
        return fields 

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