from django.urls import path
from .views import Home, RegisterAPIView

app_name = 'giftapp'

urlpatterns = [
    path("register", RegisterAPIView.as_view()),
    path("", Home.as_view()),
]
