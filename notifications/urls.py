from django.urls import path

from .views import OrganizerRegistrationNotificationsView


urlpatterns = [
    path(
        '',
        OrganizerRegistrationNotificationsView.as_view(),
        name='organizer-registration-notifications',
    ),
]
