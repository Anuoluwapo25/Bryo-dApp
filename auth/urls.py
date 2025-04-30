from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('host.urls')),  # This assumes you have a urls.py file in your 'host' app
]
