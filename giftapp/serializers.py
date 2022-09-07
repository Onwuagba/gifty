from rest_framework import serializers
from giftapp.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt import serializers as jwt_serializers
from rest_framework.exceptions import ValidationError
from django.contrib.auth import authenticate
from rest_framework.views import exceptions

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
    
class ResetPasswordSerializer(serializers.ModelSerializer):
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