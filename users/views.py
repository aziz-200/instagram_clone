import code

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import permissions, status
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from typing import cast
from shared.utils import send_email, check_email_or_phone
from .serializers import (SignUpSerializer,
                          ChangeUserInformation,
                          ChangeUsePhotoSerializer,
                          LoginSerializer,
                          LoginRefreshSerializer,
                          LogOutSerializer,
                          ForgotPasswordSerializer, ResetPasswordSerializer)

from .models import (User,
                     DONE,
                     CODE_VERIFIED,
                     VIA_PHONE,
                     VIA_EMAIL)


class CreateUserView(CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = SignUpSerializer

class VerifyUserView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        user = cast(User, self.request.user)
        code = self.request.data.get('code')
        self.check_verify(user, code)



        self.check_verify(user, code)
        return Response({
            "success": True,
            "auth_status": user.auth_status,
            "access":user.token()['access'],
            "refresh": user.token()['refresh_token']
            })



    @staticmethod
    def check_verify(user, code):
        verifies = user.verification_code.filter(expiration_time__gte=timezone.now(), code=code, is_verified=False)
        if not verifies.exists():
            data = {
                'message': 'Verification code is expired',
            }
            raise ValidationError(data)
        verifies.update(is_verified=True)
        if user.auth_status != DONE:
            user.auth_status = CODE_VERIFIED
            user.save()
        return True

class GetNewVerificationCodeView(APIView):
    permission_classes = (IsAuthenticated, )
    def get(self, request, *args, **kwargs):
        user =  self.request.user
        self.check_verification(user)
        if user.auth_type == VIA_EMAIL :
            code = user.create_verify_code(VIA_EMAIL)
            send_email(user.email, code)
            print(code)
        elif user.auth_type == VIA_PHONE:
            code = user.create_verify_code(VIA_PHONE)
            send_email(user.phone_number, code )
            print(code)
        else:
            data = {
                "success": False,
                "message": "Verification code is not expired",
            }
        return Response({
            "success": True,
            'message': 'Verification code is send again',
        })


    @staticmethod
    def check_verification(user):
        verifies = user.verification_code.filter(expiration_time__gte=timezone.now(), is_verified=False)
        if verifies.exists():
            data = {
        'message': 'Verification code is not expired',
            }
            raise ValidationError(data)


class ChangeInformationView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangeUserInformation
    http_method_names = ['patch','post']

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        super(ChangeInformationView, self).update(request, *args, **kwargs)
        data = {
            'success': True,
            'message': 'User has been updated.',
            'auth_status': self.request.user.auth_status,
        }
        return Response(data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        super(ChangeInformationView, self).update(request, *args, **kwargs)
        data = {
            'success': True,
            'message': 'User has been updated.',
            'auth_status': self.request.user.auth_status,
        }
        return Response(data, status=status.HTTP_200_OK)


class ChangeUsePhotoView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangeUsePhotoSerializer  # Klas darajasida serializer belgilab ketgan ma'qul

    def put(self, request, *args, **kwargs):
        serializer = ChangeUsePhotoSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'User photo has been updated.',
            }, status=status.HTTP_200_OK)

        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )

class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer


class LoginRefreshView(TokenRefreshView):
    serializer_class = LoginRefreshSerializer

class LogOutView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LogOutSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        try:
            refresh_token = self.requests.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            data = {
                'success': True,
                'message': 'User has been logged out.',
            }
            return Response(data, status=status.HTTP_200_OK)
        except TokenError as e:
            return Response({
                'success': False,
                'message': 'Token error',
            }, status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny,]
    serializer_class = ForgotPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        email_or_phone_number = serializer.validated_data.get('email_or_phone_number')
        user = serializer.validated_data.get('user')
        if check_email_or_phone(email_or_phone_number) == 'email':
            code = user.create_verify_code(VIA_EMAIL)
            send_email(email_or_phone_number, code)
        elif check_email_or_phone(email_or_phone_number) == 'phone_number':
            code = user.create_verify_code(VIA_PHONE)
            send_email(email_or_phone_number, code)
        return Response({
            'success': True,
            'message': 'Email has been sent.',
            'access_token': user.token()['access'],
            'refresh_token': user.token()['refresh_token'],
            'user_status': user.auth_status,
        }, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['patch', 'put']

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        response = super(ResetPasswordView, self).update(request, *args, **kwargs)
        try:
            user = User.objects.get(id = response.data.get('id'))
        except ObjectDoesNotExist as e:
            raise NotFound(detail='user not found')
        return Response({
            'success': True,
            'message': 'User\'s password has been updated.',
            'access': user.token()['access'],
            'refresh': user.token()['refresh_token'],
        })

