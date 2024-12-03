from django.urls import path
from btc_tracker import views
urlpatterns = [
    path('btc', views.btc_view, name='btc'),
]
