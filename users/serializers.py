import code

from django.contrib.auth.password_validation import validate_password
from django.core.validators import FileExtensionValidator
from django.template.context_processors import request
from phonenumbers.tzdata.data0 import data
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import IsAuthenticated

from shared.utils import check_email_or_phone, send_email
from .models import User, UserConfirmation, VIA_EMAIL, VIA_PHONE, NEW, CODE_VERIFIED, DONE, PHOTO_DONE
from rest_framework import exceptions, status
from django.db.models import Q
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class SignUpSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)

    def __init__(self, *args, **kwargs):
        super(SignUpSerializer, self).__init__(*args, **kwargs)
        self.fields['email_phone_number'] = serializers.CharField(read_only=False,
                                                                  write_only=True)


    class Meta:
        model = User
        fields = (
            'id',
            'auth_type',
            'auth_status'
        )
        extra_kwargs = {
            'auth_type' : {'read_only': True, 'required': False},
            'auth_status': {'read_only': True, 'required': False},
        }

    def create(self, validated_data):
        user: User = super(SignUpSerializer, self).create(validated_data)
        if user.auth_type == VIA_EMAIL:
            code = user.create_verify_code(VIA_EMAIL)
            send_email(user.email, code)
        elif user.auth_type == VIA_PHONE:
            code = user.create_verify_code(VIA_PHONE)
            send_email(user.email, code)
            #  BU YERDA SMS XABARNOMA JO'NATISH CHAQIRILADI
            # send_phone_code(user.phone_number)
        user.save()
        return user


    def validate(self, data):
        super(SignUpSerializer, self).validate(data)
        data = self.auth_validate(data)
        return data

    @staticmethod
    def auth_validate(data):
        user_input = str(data.get('email_phone_number')).lower()
        input_type = check_email_or_phone(user_input) # email or phone
        if input_type == 'email':
            data = {
                'email': user_input,
                'auth_type': VIA_EMAIL,
            }
        elif input_type == 'phone':
            data = {
                'phone_number': user_input,
                'auth_type': VIA_PHONE,
            }
        else:
            data = {
                'success': False,
                'message': 'Please enter a valid phone number.',
            }
            raise ValidationError(data)
        return data

    def validate_email_phone_number(self, value):
        value = value.lower()
        print(value)
        if value and User.objects.filter(email=value).exists():
            data = {
                'success': False,
                'message': 'Email already exists.',
            }
            raise ValidationError(data)
        elif value and User.objects.filter(phone_number=value).exists():
            data = {
                'success': False,
                'message': 'Phone number already exists.',
            }
            raise ValidationError(data)
        return value


    def to_representation(self, instance):
        print("to_rep", instance)
        data = super(SignUpSerializer, self).to_representation(instance)
        data.update(instance.token())
        return data

# Username va passwordni reset qilish
class ChangeUserInformation(serializers.Serializer):
    first_name = serializers.CharField(write_only=True, required=True)
    last_name = serializers.CharField(write_only=True, required=True)
    username = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        password = data.get('password', None)
        confirm_password = data.get('confirm_password', None)
        if password != confirm_password:
            raise ValidationError({
                "message": "Passwords don't match",
            })
        if password:
            validate_password(password)
            validate_password(confirm_password)
        return data

    def validate_username(self, username):
        if len(username) < 5 or len(username) > 30:
            raise ValidationError({
                "message": "Username must be between 5 and 30 characters",
            })
        if username.isdigit():
            raise ValidationError({
                "message": "Username must not be only digits",
            })
        return username

    def validate_first_name(self, first_name):
        if len(first_name) < 5 or len(first_name) > 20:
            raise ValidationError({
                "message": "First name must be between 5 and 20 characters",
            })
        if first_name.isdigit():
            raise ValidationError({
                "message": "First name cannot be  digits",
            })
        return first_name

    def validate_last_name(self, last_name):
        if len(last_name) < 5 or len(last_name) > 20:
            raise ValidationError({
                "message": "Last name must be between 5 and 20 characters",
            })
        if last_name.isdigit():
            raise ValidationError({
                "message": "Last name cannot be  digits",
            })
        return last_name

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.password = validated_data.get('password', instance.password)
        instance.username = validated_data.get('username', instance.username)
        if validated_data.get('password'):
            instance.set_password(validated_data.get('password'))
        if instance.auth_status == CODE_VERIFIED:
            instance.auth_status = DONE
        instance.save()
        return instance


class ChangeUsePhotoSerializer(serializers.Serializer):
    photo = serializers.ImageField(validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'heir', 'HEIF'])])

    def update(self, instance, validated_data):
        photo = validated_data.get('photo')
        if photo:
            instance.photo = photo
            instance.auth_status = PHOTO_DONE
            instance.save()
        return instance



