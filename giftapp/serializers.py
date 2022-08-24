from rest_framework import serializers
from giftapp.models import User
from django.contrib.auth.password_validation import validate_password

class RegistrationSerializers(serializers.ModelSerializer):
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
    
    def validate(self, data):
        if not data.get('password') or not data.get('confirm_password'):
            raise serializers.ValidationError("Please enter a password and confirm it.")
        if data.get('password') != data.get('confirm_password'):
            raise serializers.ValidationError("Your passwords do not match.")
        return data

        # if attrs['password'] != attrs['password2']:
        #     raise serializers.ValidationError({"password": "Password fields didn't match."})

        # return attrs
    
    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        
        user.set_password(validated_data['password'])
        user.save()

        return user