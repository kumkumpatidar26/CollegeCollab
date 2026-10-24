from django.urls import path
from .views import RegisterView, MyProfileView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', MyProfileView.as_view(), name='profile'),
]