from django.contrib import admin
from .models import Task


class TaskServiceAdmin(admin.ModelAdmin):
    model = Task


admin.site.register(Task, TaskServiceAdmin)
