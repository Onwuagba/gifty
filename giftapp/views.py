# from django.shortcuts import render
from base64 import urlsafe_b64decode
from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from giftapp.models import User
from giftapp.serializers import ChangePasswordSerializer, CustomTokenSerializer, PasswordResetSerializer, RegistrationSerializer, ResetPasswordSerializer
from rest_framework_simplejwt import views as jwt_views
import json
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.contrib.auth.tokens import default_token_generator 

# Create your views here.   

class Home(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args):
        user_name = request.user.first_name
        res = {
            'message': f"Welcome {user_name}",
            'error': []
        }
        return Response(res, status=status.HTTP_200_OK)

# Registration 
class RegisterAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # change_serializer.save()
            res = 'Registration successful. Please confirm your email to complete set up'
            re_status = 'success'
            res_status = status.HTTP_200_OK
        except Exception as e:
            res = serializer.errors
            re_status = 'failure'
            res_status = status.HTTP_400_BAD_REQUEST
        
        return JsonResponse({
                'message':res,
                'status':re_status,
            }, status=res_status)

        # if serializer.is_valid(raise_exception=True):
        #     serializer.save()

        #     return Response({
        #         'message':"res",
        #         'status':'re_status',
        #     })
    
# Change password 
class ChangePasswordView(generics.UpdateAPIView):
    """
    Allow authenticated user to change password

    Accepts - password, confirm_password, old_password
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordSerializer

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def patch(self, request, **kwargs):
        user = self.get_object()
        change_data = request.data
        # change_data['user'] = request.user
        change_serializer = self.serializer_class(user, data=change_data)
        try:
            change_serializer.is_valid(raise_exception=True)
            change_serializer.save()
            res = 'Password reset is complete. Please check your email to complete process'
            re_status = 'success'
            res_status = status.HTTP_200_OK
        except Exception:
            res = change_serializer.errors
            re_status = 'failure'
            res_status = status.HTTP_400_BAD_REQUEST

        return JsonResponse({
            'message':res,
            'status':re_status,
            }, status=res_status)

# Reset/Forgot password 
class ResetPasswordView(APIView):
    """
    Allow user to reset password.
    User clicks forgot password and enters email for validation. Email is sent with token
    Accepts - email
    """
    permission_classes = (AllowAny,)
    serializer_class = ResetPasswordSerializer

    def post(self, request, **kwargs):
        reset_data = request.data
        try:
            change_serializer = self.serializer_class(data=reset_data)
            if change_serializer.is_valid(raise_exception=True):
                change_serializer.create_token_send_email(request)
                res = f"A password reset link has been sent to {reset_data['email']}. Check your inbox to complete the process."
                re_status = 'success'
                res_status = status.HTTP_200_OK
            else:
                for error in change_serializer.errors:
                    res = error
                re_status = 'failed'
                res_status = status.HTTP_400_BAD_REQUEST
        except Exception as e:
            res = e.args[0]
            re_status = 'failed'
            res_status = status.HTTP_400_BAD_REQUEST

        return JsonResponse({
            'message':res,
            'status':re_status,
            }, status=res_status)


class PasswordResetView(generics.UpdateAPIView):
    """
    Users come here after submitting mail from forgot password API.
    User clicks link from email and submits new password
    * Accepts - email
    """
    permission_classes = (AllowAny,)
    serializer_class = PasswordResetSerializer

    def get_object(self, uid, token):
        error = {}
        if not all([uid, token]):
            error['new_password'] = "Reset password link has expired. Please begin the forgot password process again"
        else:
            uid = urlsafe_b64decode(uid).decode('utf-8')
            try:
                user = User.objects.get(uid=uid)
                if not default_token_generator.check_token(user, token):
                    error['new_password'] = "Reset password link has expired. Please begin the forgot password process again"
            except Exception:
                error['new_password'] = "No user found with user ID"

        if error:
            raise ValidationError(error)
        return user 

    def patch(self, request, **kwargs):
        uid =  kwargs.get('g_uid', "")
        token = kwargs.get('token', "")
        context = {
            "uid":uid,
            "token":token
        }
        try:
            user = self.get_object(uid, token)
            data = request.data
            pass_reset_serializer = self.serializer_class(user, data=data, context=context)
            if pass_reset_serializer.is_valid(raise_exception=True):
                pass_reset_serializer.save()
                res = "Password reset is complete. Please proceed to login"
                re_status = 'success'
                res_status = status.HTTP_200_OK
            else:
                for error in pass_reset_serializer.errors:
                    res = error
                re_status = 'faiwled'
                res_status = status.HTTP_400_BAD_REQUEST
        except Exception as e:
            res = e.args[0]
            re_status = 'failed'
            res_status = status.HTTP_400_BAD_REQUEST

        return JsonResponse({
            'message':res,
            'status':re_status,
            }, status=res_status)

# customise JWT login payload to pass firstname and other information
class CustomToken(jwt_views.TokenObtainPairView):

    serializer_class = CustomTokenSerializer
    token_obtain_pair = jwt_views.TokenObtainPairView.as_view()


# class Logout(APIView):
#     permission_classes = (AllowAny,)
#     def get(self,request):
#         import pdb
#         pdb.set_trace()
#         request.user.auth_token.delete()
#         auth.logout(request)
#         return Response('successfully deleted')