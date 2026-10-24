from django.urls import path
from .views import CollegeListCreateView


urlpatterns = [
    path('', CollegeListCreateView.as_view(), name='college-list-create'),
]