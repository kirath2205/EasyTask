from functools import wraps

import jwt
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from django.contrib.auth import get_user_model
from django.http import JsonResponse
# noinspection PyUnresolvedReferences
from drf_yasg import openapi
# noinspection PyUnresolvedReferences
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
# noinspection PyUnresolvedReferences
from rest_framework_simplejwt.tokens import RefreshToken
from allauth.socialaccount.providers.oauth2.client import OAuth2Client

from .models import Auth
from .serializers import AuthModelSerializer
from django.conf import settings


@swagger_auto_schema(
    method='get',
    responses={200: 'OK'},
    operation_summary='UserAuth APIs',
    operation_description='APIs for user-auth service',
    manual_parameters=[
    ],
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_users_without_jwt(request):
    data = Auth.objects.all()
    serializer = AuthModelSerializer(data, many=True)
    return Response(serializer.data)


@swagger_auto_schema(
    method='get',
    responses={200: 'OK'},
    operation_summary='Get All users(requires JWT)',
    operation_description='APIs for user-auth service',
    manual_parameters=[
    ],
)
@api_view(['GET'])
def get_all_users_with_jwt(request):
    data = Auth.objects.all()
    serializer = AuthModelSerializer(data, many=True)
    return Response(serializer.data)


@swagger_auto_schema(
    method='post',
    responses={201: 'CREATED', 400: 'BAD REQUEST'},
    operation_summary='Register a user',
    operation_description='APIs for user-auth service',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
            'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username'),
            'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email address'),
            'mobile_number': openapi.Schema(type=openapi.TYPE_STRING, description='Mobile Number'),
        },
        required=['password', 'username', 'email', 'mobile_number']
    ),
)
@api_view(['POST'])
@permission_classes([AllowAny])
def create_user(request):
    user_payload = AuthModelSerializer(data=request.data)
    if user_payload.is_valid():
        user = user_payload.save()
        token_data = __get_tokens_for_user(user)
        return Response({'message': 'User created successfully', 'token': token_data}, status=status.HTTP_201_CREATED)
    else:
        return Response(user_payload.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='post',
    responses={200: 'OK', 400: 'BAD REQUEST'},
    operation_summary='User Login',
    operation_description='APIs for user-auth service',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
            'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email address'),
        },
        required=['password', 'email']
    ),
)
@api_view(['POST'])
@permission_classes([AllowAny])
def user_login(request):
    user = AuthModelSerializer().get_user_by_email(email=request.data.get('email', ''))
    if user and user.check_password(request.data.get('password', '')):
        return Response(__get_tokens_for_user(user), status=status.HTTP_200_OK)
    else:
        return Response({'message': 'Invalid Credentials'})


def __get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def jwt_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        User = get_user_model()
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return JsonResponse({'error': 'Authorization header missing'}, status=401)

        try:
            # Expecting header format: "Bearer <token>"
            prefix, token = auth_header.split(' ')
            if prefix.lower() != 'bearer':
                return JsonResponse({'error': 'Invalid token prefix'}, status=401)

            # Decode the token using your Django SECRET_KEY and expected algorithm(s)
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')
            if not user_id:
                return JsonResponse({'error': 'Invalid token payload'}, status=401)

            # Fetch the user from the database
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return JsonResponse({'error': 'User not found'}, status=404)

            # Attach the user to the request object
            request.user = user
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expired'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Invalid token'}, status=401)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=401)

        return view_func(request, *args, **kwargs)

    return _wrapped_view


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = settings.GOOGLE_CALLBACK_URL
    client_class = OAuth2Client
