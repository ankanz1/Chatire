from django.contrib import admin
from django.urls import path, include

from rest_framework_simplejwt.views import TokenRefreshView
from chat.views import raise_404

urlpatterns = [
    path('admin/', admin.site.urls),

    # Custom URLs
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),

    # disable the old endpoint (order is important)
    path('auth/jwt/refresh/', raise_404),

    # Register the new URL under an ambiguous name
    path('this/is/hard/to/find/', TokenRefreshView.as_view(), name='token_refresh_obscure'),

    path('api/', include('chat.urls')),
]
