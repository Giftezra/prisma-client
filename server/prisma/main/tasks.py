from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import requests


@shared_task
def send_booking_confirmation_email(user_email, booking_id, vehicle_name):
    """
    Send booking confirmation email to user
    """
    subject = f'Booking Confirmation - #{booking_id}'
    message = f'Your booking has been confirmed for {vehicle_name} with Booking ID: {booking_id}'
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            fail_silently=False,
        )
        return f"Email sent successfully to {user_email}"
    except Exception as e:
        return f"Failed to send email: {str(e)}"


@shared_task
def process_payment_webhook(webhook_data):
    """
    Process Stripe webhook data asynchronously
    """
    # Add your webhook processing logic here
    print(f"Processing webhook: {webhook_data}")
    return "Webhook processed successfully"


@shared_task
def cleanup_expired_bookings():
    """
    Clean up expired or cancelled bookings
    """
    from .models import BookedAppointment
    from django.utils import timezone
    from datetime import timedelta
    
    # Delete bookings older than 30 days that are cancelled or completed
    cutoff_date = timezone.now() - timedelta(days=30)
    deleted_count = BookedAppointment.objects.filter(
        created_at__lt=cutoff_date,
        status__in=['cancelled', 'completed']
    ).delete()[0]
    
    return f"Cleaned up {deleted_count} expired bookings"

""" Check for the detailers availability by sending the job data via api to the detailer app.
    The detailer app would then respond with the availability of the detailer.
    ARGs {
        "service_type" : string,
        "valet_type" : string,
        "booking_date" : string,
        'booking_reference'
    }
     The service type contains on the detailer app only needs the name of the service type, as it has its own internal service type with the same name and would check the duration of the service type.
     RESPONSE : {
        "detailer_id" : string,
        'available_time': [
            {
                'start_time': string,
                'end_time': string,
            }
        ]
        given the service type, the detailer app would respond with the available time for the detailer.
    }

 """
@shared_task
def check_detailers_availability(service_type, valet_type, booking_date, booking_reference):
    main_url = settings.DETAILER_API_URL
    detailer_api_url = f"{main_url}/?service_type={service_type}&valet_type={valet_type}&booking_date={booking_date}&booking_reference={booking_reference}"
    response = requests.get(detailer_api_url)
    return response.json()
