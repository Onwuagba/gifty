from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from giftapp.serializers import RegistrationSerializers

# Create your views here.

def getToken(username, password):
    payload = {
        'username':username,
        'password':password
    }
    pass

class RegisterAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializers

    def post(self, request):
        user = request.data.get('user', {})
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)