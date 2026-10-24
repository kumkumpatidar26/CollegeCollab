from django.urls import path
from .views import home, events, dashboard

urlpatterns = [
    path('', home, name='home'),
    path('events/', events, name='events'),
    path('dashboard/', dashboard, name='dashboard'),
]