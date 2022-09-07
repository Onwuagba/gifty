# from django.shortcuts import render
from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from giftapp.serializers import ChangePasswordSerializer, CustomTokenSerializer, RegistrationSerializer, ResetPasswordSerializer
from rest_framework_simplejwt import views as jwt_views
import json
from django.http import JsonResponse

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
        self.object = self.get_object()
        change_data = request.data
        change_data['user'] = request.user
        change_serializer = self.serializer_class(change_data['user'], data=change_data)
        try:
            change_serializer.is_valid(raise_exception=True)
            change_serializer.save()
            res = 'Password reset is complete.'
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
class ResetPasswordView(generics.UpdateAPIView):
    """
    Allow user to reset password.

    User clicks forgot password and enters email for validation. Email is sent with token
    
    Accepts - password, confirm_password, old_password
    """
    permission_classes = (AllowAny,)
    serializer_class = ResetPasswordSerializer

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def patch(self, request, **kwargs):
        self.object = self.get_object()
        change_data = request.data
        change_data['user'] = request.user
        change_serializer = self.serializer_class(change_data['user'], data=change_data)
        try:
            change_serializer.is_valid(raise_exception=True)
            change_serializer.save()
            res = 'Password reset is complete.'
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

# # Reset and forgot password 
# class ResetPasswordView(APIView):
#     # no permission class so we can do reset and change password in the same class
#     serializer_class = RegistrationSerializers

#     def post(self, request, **kwargs):
#         data = request.data

#         if request.user.is_authenticated and kwargs.get('change_type')=='change_password':
#             if request.user.is_admin: # allow admin change user password
#                 user = data.get('user_id')
#             else: 
#                 user = request.user
            
#             data['user'] = user
#             reset = self.change_password(data)

#             return Response({
#                 'message':'Registration successful. Please confirm your email to complete set up',
#                 # 'firstname': serializer.data.get('first_name'),
#                 # 'email': serializer.data.get('email'),
#             }, status=status.HTTP_201_CREATED)

#         elif request.user.is_authenticated==False and kwargs.get('change_type')=='forgot_password':
            
#             return Response({
#                 'message':'',
#                 'errors':[
#                     'Please'
#                 ]
#             }, status=status.HTTP_201_CREATED)
        
#         else:
#             pass
    
#     def change_password(self, data):
#         change_serializer = self.serializer_class(data=data)
#         change_serializer.is_valid(raise_exception=True)
#         change_serializer.save()

#         return change_serializer

#     def forgot_password(self, data):
#         forgot_password = self.serializer_class(data=data)
#         forgot_password.is_valid(raise_exception=True)
#         forgot_password.save()

#         return forgot_password

# customise JWT login payload to pass firstname and other information
class CustomToken(jwt_views.TokenObtainPairView):

    serializer_class = CustomTokenSerializer
    token_obtain_pair = jwt_views.TokenObtainPairView.as_view()