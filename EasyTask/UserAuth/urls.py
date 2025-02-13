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
        title="UserAuth service",
        default_version='v1',
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("getUsers", views.get_all_users_without_jwt, name="GetAllUsers"),
    path('token/obtain/', jwt_views.TokenObtainPairView.as_view(), name='token_create'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('getUsersWithPermission', views.get_all_users_with_jwt, name='GetAllusersWithPermissions'),
    path('createUser', views.create_user, name='CreateUser'),
    path('userLogin', views.user_login, name='UserLogin')
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
