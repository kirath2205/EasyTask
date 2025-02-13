from django.contrib import admin
from .models import Auth
class UserAuthAdmin(admin.ModelAdmin):
    model = Auth

admin.site.register(Auth, UserAuthAdmin)