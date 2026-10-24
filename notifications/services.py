import logging
from smtplib import SMTPException

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.template.loader import render_to_string


logger = logging.getLogger(__name__)


def _deliver_email(subject, message, recipient, event_id, notification_type):
    try:
        sent_count = send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient],
            fail_silently=False,
        )
    except (OSError, SMTPException):
        logger.warning(
            "Could not deliver %s notification for event_id=%s.",
            notification_type,
            event_id,
        )
        return

    if sent_count != 1:
        logger.warning(
            "Could not deliver %s notification for event_id=%s.",
            notification_type,
            event_id,
        )


def _queue_email(template_name, subject, context, recipient, event_id, notification_type):
    if not recipient:
        return

    message = render_to_string(
        f'notifications/{template_name}.txt',
        context,
    )
    transaction.on_commit(
        lambda: _deliver_email(
            subject,
            message,
            recipient,
            event_id,
            notification_type,
        )
    )


def _event_context(event):
    return {
        'event_title': event.title,
        'event_date': event.date,
        'event_start_time': event.start_time,
        'event_end_time': event.end_time,
        'event_venue': event.venue,
    }


def queue_registration_confirmation(registration):
    context = _event_context(registration.event)
    context['student_name'] = (
        registration.student.first_name or registration.student.username
    )
    _queue_email(
        'registration_confirmation',
        'Event registration confirmed: ' + registration.event.title,
        context,
        registration.student.email,
        registration.event_id,
        'registration confirmation',
    )


def queue_registration_cancellation(registration):
    context = _event_context(registration.event)
    context['student_name'] = (
        registration.student.first_name or registration.student.username
    )
    _queue_email(
        'registration_cancellation',
        'Event registration cancelled: ' + registration.event.title,
        context,
        registration.student.email,
        registration.event_id,
        'registration cancellation',
    )


def queue_event_notification(event, recipients, cancelled=False):
    context = _event_context(event)
    if cancelled:
        template_name = 'event_cancellation'
        subject = 'Event cancelled: ' + event.title
        notification_type = 'event cancellation'
    else:
        template_name = 'event_update'
        subject = 'Event updated: ' + event.title
        notification_type = 'event update'

    for recipient in set(recipients):
        _queue_email(
            template_name,
            subject,
            context,
            recipient,
            event.pk,
            notification_type,
        )
