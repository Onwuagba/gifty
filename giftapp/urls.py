from django.urls import path
from .views import ChangePasswordView, Home, RegisterAPIView

app_name = 'giftapp'

urlpatterns = [
    path("register", RegisterAPIView.as_view()),
    path("change_password", ChangePasswordView.as_view()),
    path("", Home.as_view()),
]
