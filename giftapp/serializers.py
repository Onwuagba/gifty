from base64 import urlsafe_b64encode
from rest_framework import serializers
from giftapp.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt import serializers as jwt_serializers
from rest_framework.exceptions import ValidationError
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator 
from rest_framework.views import exceptions
from giftapp.utilities.constants import email_sender
from giftapp.utilities.mail.send_mail import send_mail_now
from base64 import urlsafe_b64decode

class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True,
        required=True, 
        validators=[validate_password]
    )
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'confirm_password', 'first_name', 'last_name']
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }
    
    # def is_valid(self, raise_exception=False):
    #     reg = super(RegistrationSerializer, self).is_valid(False)
    #     if self._errors:
    #         if raise_exception:
    #             raise ValidationError(self.errors)
    #     return reg
    
    def validate(self, data):
        error = {}
        if not data.get('password') or not data.get('confirm_password'):
            error["password"] = "Please enter a password and confirm it"
        if data.get('password') != data.get('confirm_password'):
            error["password"] = "Your passwords do not match"

        if error:
            raise serializers.ValidationError(error)
        return data
    
    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        
        user.set_password(validated_data['password'])
        user.save()

        return user


class ChangePasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)
    old_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('old_password', 'password', 'confirm_password')

    def validate(self, data):
        error = {}
        user = self._kwargs['data']['user']

        if not data.get('password') or not data.get('confirm_password'):
            error["password"] = "Please enter a password and confirm it."
        if data.get('password') != data.get('confirm_password'):
            error["password"] = "Your passwords do not match"
        if not user.check_password(data.get('old_password')):
            error["password"] = "Your old password is not valid"
        if data.get('password') == data.get('old_password'):
            error["password"] = "New password cannot be same as old password"
        
        if error:
            raise serializers.ValidationError(error)

        data.pop('old_password')
        data.pop('confirm_password')
        return data

    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()

        return instance
    
class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, data):

        try:
            user = User.objects.get(email=data)
            return user
        except Exception:
            raise serializers.ValidationError("No account found with this email address")

    def create_token_send_email(self, request):
        email_content = {}
        user = self.validated_data['email']
        token = default_token_generator.make_token(user)
        uid = urlsafe_b64encode(bytes(str(user.uid), "utf-8")).decode("utf-8")

        email_content['subject'] = 'Reset password email verification'
        email_content['sender'] = email_sender
        email_content['recipient'] = user.email
        email_content['template'] = 'reset_password.html'
        reset_url = request.build_absolute_uri(f'password_reset/{uid}/{token}')
        context = {
            'name': user.first_name,
            'url': reset_url
        }

        send_reset_mail, result = send_mail_now(email_content, context)
        if not result:
            raise serializers.ValidationError(send_reset_mail)
        return True


class PasswordResetSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True,
        required=True, 
        validators=[validate_password]
    )
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        error = {}
        if not data.get('new_password') or not data.get('confirm_password'):
            error["new_password"] = "Please enter a password and confirm it"
        if data.get('new_password') != data.get('confirm_password'):
            error["new_password"] = "Your passwords do not match"

        if error:
            raise serializers.ValidationError(error)
        return data

    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        instance.save()

        return instance

class CustomTokenSerializer(jwt_serializers.TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['is_superuser'] = user.is_superuser
        return token
    
    def validate(self, attrs):
        error = {}
        authenticate_kwargs = {
            self.username_field: attrs[self.username_field],
            'password': attrs['password'],
        }
        try:
            authenticate_kwargs['request'] = self.context['request']
        except KeyError:
            pass
        self.user = authenticate(**authenticate_kwargs)
        if self.user is None or not self.user.is_active:
            error['message'] = 'No account found with this credential'
            error['status'] = 'Failed'
            raise exceptions.AuthenticationFailed(error)
        return super().validate(attrs)