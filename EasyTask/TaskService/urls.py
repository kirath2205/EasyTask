from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from . import views
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from drf_yasg import openapi
from rest_framework_simplejwt import views as jwt_views

schema_view = get_schema_view(
    openapi.Info(
        title="Task service",
        default_version='v1',
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("createTask", views.create_task, name="CreateTask"),
    path("getCurrentTasks", views.get_current_tasks, name="GetCurrentTasks")
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
