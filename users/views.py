from django.shortcuts import render
from rest_framework import permissions, status
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError

from shared.utils import send_email
from .serializers import SignUpSerializer, ChangeUserInformation, ChangeUsePhotoSerializer
from typing import cast
from .models import User, DONE, CODE_VERIFIED, VIA_PHONE, VIA_EMAIL


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
        # request.user (instance) ni birinchi argument sifatida uzatamiz
        serializer = ChangeUsePhotoSerializer(request.user, data=request.data, partial=True)

        if serializer.is_valid():
            # .save() metodini chaqiramiz, u o'zi ichkarida update() ni ishga tushiradi
            serializer.save()

            return Response({
                'success': True,
                'message': 'User photo has been updated.',
            }, status=status.HTTP_200_OK)

        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )