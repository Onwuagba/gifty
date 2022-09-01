from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt import views as jwt_views

from giftapp.views import CustomToken

schema_view = get_schema_view(
   openapi.Info(
      title="Gifty API",
      default_version='v1',
      description="A gift collection API",
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('d-admin/', admin.site.urls),
    path('myadmin/', include('giftadmin.urls')),
    #documentation
    path('doc/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # path('doc/', schema_view),
    path('api/v1/', include('giftapp.urls')),
    
    #authentication
    path('api/v1/get_token/', CustomToken.as_view(), name='token_obtain_pair'),
    path('api/v1/refresh_token/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
]