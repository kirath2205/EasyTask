from django.conf import settings

from . import views
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

urlpatterns = [
    path("createPrivateTask", views.create_private_task, name="CreatePrivateTask"),
    path("getSubscriptions", views.get_subscriptions, name="GetSubscriptions"),
    path("submitProof", views.submit_proof, name="SubmitProof"),
    path("createPublicTask", views.create_public_task, name="CreatePublicTask"),
    path("subscribeTask", views.subscribe_task, name="SubscribeTask"),
    path("getMilestone", views.get_milestone, name="GetMilestone"),
    path("getPublicTasks", views.get_public_tasks, name="GetPublicTasks")
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
