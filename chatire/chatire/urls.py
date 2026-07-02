from django.contrib import admin
from django.urls import path, include

from rest_framework_jwt.views import refresh_jwt_token
from chat.views import raise_404

urlpatterns = [
    path('admin/', admin.site.urls),

    # Custom URLs
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),

    # disable the old endpoint (order is important)
    path('auth/jwt/refresh/', raise_404),

    # Register the new URL under an ambiguous name
    path('this/is/hard/to/find/', refresh_jwt_token),

    path('api/', include('chat.urls')),
]
