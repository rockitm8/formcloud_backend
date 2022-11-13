from django.contrib import admin

from users.models import User
# Register your models here.

class SettingUser(admin.ModelAdmin):
  list_display = ('id', 'user_name', 'email', 'first_name', 'last_name')

admin.site.register(User, SettingUser)