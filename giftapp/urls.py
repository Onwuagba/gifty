from django.urls import path, re_path
from .views import ChangePasswordView, Home, RegisterAPIView, ResetPasswordView, PasswordResetView, Logout

app_name = 'giftapp'

urlpatterns = [
    path("register", RegisterAPIView.as_view()),
    path("reset_password", ChangePasswordView.as_view()),
    path("forgot_password", ResetPasswordView.as_view()),
    path("password_reset/<g_uid>/<token>", PasswordResetView.as_view()),
    path("logout", Logout.as_view()),
    # re_path(r'^password_reset/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/$', ResetPasswordView.as_view()),
    path("", Home.as_view()),
]
