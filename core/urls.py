# btc_tracker/urls.py

from django.contrib import admin
from django.urls import path
from crypto_tracker.views import main_view  # Import the view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', main_view, name='main'),  # Add the main view to the root URL
]
