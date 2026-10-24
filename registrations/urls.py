from django.urls import path
from .views import (
    RegistrationCreateView,
    MyRegistrationsView,
    EventRegistrationsView ,
    RegistrationDeleteView
)
\

urlpatterns = [
    path('', RegistrationCreateView.as_view(), name='registration-create'),
    path('my/', MyRegistrationsView.as_view(), name='my-registrations'),
    path(
        'event/<int:event_id>/',
        EventRegistrationsView.as_view(),
        name='event-registrations'
    ),
    
    path(
    '<int:pk>/cancel/',
    RegistrationDeleteView.as_view(),
    name='registration-cancel'
),
]