from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
# noinspection PyUnresolvedReferences
from rest_framework_simplejwt.tokens import RefreshToken
# noinspection PyUnresolvedReferences
from drf_yasg.utils import swagger_auto_schema
# noinspection PyUnresolvedReferences
from drf_yasg import openapi

from .models import Auth
from .serializers import AuthModelSerializer



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
    if user.check_password(request.data.get('password', '')):
        return Response(__get_tokens_for_user(user), status=status.HTTP_200_OK)
    else:
        return Response({'message': 'Invalid Credentials'})


def __get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }



'''
TODO: Create a view to sign up a user( create user using 
That entry would be added to profile model so that we can update that once profile payload is available

Add fields for OTP and email verification

Setup twilio api
'''
