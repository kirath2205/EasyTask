from django.conf import settings

from . import views
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static



urlpatterns = [
    path("createPrivateTask", views.create_private_task, name="CreatePrivateTask"),
    path("testRedis", views.test_redis, name="test_redis"),
    path("getSubscriptions", views.get_subscriptions, name="GetSubscriptions")
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)