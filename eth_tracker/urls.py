from django.urls import path
from eth_tracker import views
urlpatterns = [
    path('eth', views.eth_view, name='eth'),
]
