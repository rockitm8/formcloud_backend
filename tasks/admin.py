from django.contrib import admin

from tasks.models import Domain, Preset, Task

# Register your models here.
class SettingTask(admin.ModelAdmin):
  list_display = ('id', 'task_name', 'status', 'finished_date', 'first_name', 'last_name', 'email', 'subject', 'phone_number', 
  'company', 'department', 'address')

class SettingPreset(admin.ModelAdmin):
  list_display = ('id', 'user', 'preset_name', 'first_name', 'last_name', 'email', 'subject', 'phone_number', 
  'company', 'department', 'address')

class SettingDomain(admin.ModelAdmin):
  list_display = ('id', 'task', 'domain_name', 'reached_at', 'status', 'contact_page', 'emails_found', 
  'contact_form', 'form_sent', 'went_over_manually', 'sent_manually')

admin.site.register(Task, SettingTask)
admin.site.register(Preset, SettingPreset)
admin.site.register(Domain, SettingDomain)
