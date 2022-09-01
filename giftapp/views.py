from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from giftapp.serializers import CustomTokenSerializer, RegistrationSerializers
from rest_framework_simplejwt import views as jwt_views

# Create your views here.

class Home(APIView):

    def get(self, *args):
        return Response({
            'message':'Enter home',
            'error': []
        })

class RegisterAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializers

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            'message':'Registration completed',
            'firstname': serializer.data.get('first_name'),
            'email': serializer.data.get('email'),
        }, status=status.HTTP_201_CREATED)

# customise login payload to pass firstname 
class CustomToken(jwt_views.TokenObtainPairView):

    serializer_class = CustomTokenSerializer
    token_obtain_pair = jwt_views.TokenObtainPairView.as_view()