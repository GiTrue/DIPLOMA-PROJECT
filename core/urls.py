from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Подключаем api с namespace 'backend'
    path('api/v1/', include('backend.urls', namespace='backend')),
]