"""
Celery tasks for Hotel Booking Engine
Handles asynchronous operations like email sending, reminders, and cleanup
"""

from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
import logging

from bookings.models import Booking

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_confirmation_email_async(self, booking_id):
    """
    Send booking confirmation email asynchronously.
    Has retry logic for failed email attempts.
    
    Args:
        booking_id: ID of the booking
    """
    try:
        booking = Booking.objects.get(id=booking_id)
        
        subject = f'Booking Confirmation - {booking.booking_id}'
        
        context = {
            'booking': booking,
            'guest_name': booking.guest_full_name(),
            'hotel_name': booking.hotel.name,
            'room_name': f"{booking.room.room_type.name} #{booking.room.room_number}",
            'check_in_date': booking.check_in_date,
            'check_out_date': booking.check_out_date,
            'total_amount': booking.total_amount,
            'booking_reference': booking.booking_id,
            'adults': booking.adults,
            'children': booking.children,
        }
        
        html_message = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">
                    Booking Confirmation ✓
                </h2>
                
                <p>Dear {context['guest_name']},</p>
                
                <p>Thank you for your booking! Your reservation has been <strong>confirmed</strong>.</p>
                
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="color: #2c3e50; margin-top: 0;">Booking Details</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px 0; font-weight: bold; width: 40%;">Booking Reference:</td>
                            <td style="padding: 8px 0; font-family: monospace; font-size: 14px;">{context['booking_reference']}</td>
                        </tr>
                        <tr style="background-color: #f0f0f0;">
                            <td style="padding: 8px 0; font-weight: bold;">Hotel:</td>
                            <td style="padding: 8px 0;">{context['hotel_name']}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; font-weight: bold;">Room:</td>
                            <td style="padding: 8px 0;">{context['room_name']}</td>
                        </tr>
                        <tr style="background-color: #f0f0f0;">
                            <td style="padding: 8px 0; font-weight: bold;">Check-in:</td>
                            <td style="padding: 8px 0;">{context['check_in_date']}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; font-weight: bold;">Check-out:</td>
                            <td style="padding: 8px 0;">{context['check_out_date']}</td>
                        </tr>
                        <tr style="background-color: #f0f0f0;">
                            <td style="padding: 8px 0; font-weight: bold;">Guests:</td>
                            <td style="padding: 8px 0;">{context['adults']} Adults, {context['children']} Children</td>
                        </tr>
                        <tr style="font-size: 16px; color: #27ae60;">
                            <td style="padding: 12px 0; font-weight: bold;">Total Amount:</td>
                            <td style="padding: 12px 0; font-weight: bold;">${context['total_amount']}</td>
                        </tr>
                    </table>
                </div>
                
                <div style="background-color: #e8f5e8; padding: 15px; border-radius: 5px; border-left: 4px solid #27ae60;">
                    <p style="margin: 0;"><strong>✓ Important:</strong> Please keep this confirmation email for your records. You will need your booking reference for check-in.</p>
                </div>
                
                <p style="margin-top: 30px;">
                    We look forward to welcoming you to <strong>{context['hotel_name']}</strong>!
                </p>
                
                <p>If you have any questions or need to modify your booking, please contact us.</p>
                
                <p>Best regards,<br>
                <strong>The Hotel Booking Team</strong></p>
                
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
                <p style="font-size: 11px; color: #999;">
                    This is an automated message. Please do not reply to this email.<br>
                    For support, visit our website or contact customer service.
                </p>
            </div>
        </body>
        </html>
        """
        
        plain_message = f"""
        Booking Confirmation
        
        Dear {context['guest_name']},
        
        Thank you for your booking! Your reservation has been confirmed.
        
        Booking Details:
        - Booking Reference: {context['booking_reference']}
        - Hotel: {context['hotel_name']}
        - Room: {context['room_name']}
        - Check-in: {context['check_in_date']}
        - Check-out: {context['check_out_date']}
        - Guests: {context['adults']} Adults, {context['children']} Children
        - Total Amount: ${context['total_amount']}
        
        Please keep this confirmation email for your records.
        
        We look forward to welcoming you!
        
        Best regards,
        The Hotel Booking Team
        """
        
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@hotelbooking.com')
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=from_email,
            recipient_list=[booking.guest_email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Confirmation email sent for booking {booking.booking_id}")
        return f"Confirmation email sent for {booking.booking_id}"
        
    except Booking.DoesNotExist:
        logger.error(f"Booking {booking_id} not found")
        return f"Booking {booking_id} not found"
    except Exception as e:
        logger.error(f"Error sending confirmation email for booking {booking_id}: {str(e)}")
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@shared_task(bind=True, max_retries=3)
def send_cancellation_email_async(self, booking_id):
    """
    Send booking cancellation email asynchronously.
    
    Args:
        booking_id: ID of the cancelled booking
    """
    try:
        booking = Booking.objects.get(id=booking_id)
        
        subject = f'Booking Cancellation Confirmation - {booking.booking_id}'
        
        context = {
            'guest_name': booking.guest_full_name(),
            'hotel_name': booking.hotel.name,
            'booking_reference': booking.booking_id,
            'total_amount': booking.total_amount,
            'cancellation_date': timezone.now().date(),
        }
        
        html_message = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #e74c3c; border-bottom: 2px solid #e74c3c;">
                    Booking Cancelled
                </h2>
                <p>Dear {context['guest_name']},</p>
                <p>We confirm that your booking <strong>{context['booking_reference']}</strong> has been cancelled.</p>
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>Hotel:</strong> {context['hotel_name']}</p>
                    <p><strong>Cancellation Date:</strong> {context['cancellation_date']}</p>
                    <p><strong>Original Amount:</strong> ${context['total_amount']}</p>
                </div>
                <div style="background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; border-radius: 5px;">
                    <p><strong>Refund Information:</strong> Refunds will be processed within 5-7 business days.</p>
                </div>
                <p>We hope to serve you again in the future!</p>
                <p>Best regards,<br>The Hotel Booking Team</p>
            </div>
        </body>
        </html>
        """
        
        plain_message = f"""
        Booking Cancellation Confirmation
        
        Dear {context['guest_name']},
        
        We confirm that your booking {context['booking_reference']} has been successfully cancelled.
        
        Hotel: {context['hotel_name']}
        Cancellation Date: {context['cancellation_date']}
        Original Amount: ${context['total_amount']}
        
        Refund Information: Refunds will be processed within 5-7 business days.
        
        We hope to welcome you again in the future!
        
        Best regards,
        The Hotel Booking Team
        """
        
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@hotelbooking.com')
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=from_email,
            recipient_list=[booking.guest_email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Cancellation email sent for booking {booking.booking_id}")
        
    except Exception as e:
        logger.error(f"Error sending cancellation email for booking {booking_id}: {str(e)}")
        raise self.retry(exc=e)


@shared_task
def send_check_in_reminders():
    """
    Send check-in reminders 24 hours before check-in date.
    Runs daily via Celery Beat.
    """
    tomorrow = timezone.now().date() + timedelta(days=1)
    
    upcoming_bookings = Booking.objects.filter(
        check_in_date=tomorrow,
        status='confirmed'
    )
    
    for booking in upcoming_bookings:
        try:
            subject = f'Check-in Reminder - {booking.booking_id}'
            message = f"""
            Hi {booking.guest_full_name()},
            
            This is a friendly reminder that your check-in at {booking.hotel.name} is tomorrow at 3:00 PM.
            
            Booking Reference: {booking.booking_id}
            
            See you soon!
            """
            
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@hotelbooking.com')
            send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=[booking.guest_email],
            )
            
            logger.info(f"Check-in reminder sent for booking {booking.booking_id}")
        except Exception as e:
            logger.error(f"Failed to send check-in reminder for booking {booking.booking_id}: {str(e)}")
    
    return f"Check-in reminders sent for {upcoming_bookings.count()} bookings"


@shared_task
def check_pending_booking_expiry():
    """
    Expire pending bookings older than 24 hours.
    Runs every 30 minutes via Celery Beat.
    """
    expiry_time = timezone.now() - timedelta(hours=24)
    
    expired_bookings = Booking.objects.filter(
        status='pending',
        created_at__lt=expiry_time
    )
    
    count = expired_bookings.count()
    expired_bookings.update(status='cancelled')
    
    logger.info(f"Expired {count} pending bookings older than 24 hours")
    return f"Expired {count} pending bookings"


@shared_task
def cleanup_cancelled_bookings():
    """
    Archive or clean up cancelled bookings older than 30 days.
    Runs daily at 2 AM via Celery Beat.
    """
    cleanup_date = timezone.now().date() - timedelta(days=30)
    
    old_cancelled = Booking.objects.filter(
        status='cancelled',
        updated_at__date__lt=cleanup_date
    )
    
    count = old_cancelled.count()
    old_cancelled.delete()  # Or mark as archived instead of deleting
    
    logger.info(f"Cleaned up {count} old cancelled bookings")
    return f"Cleaned up {count} old cancelled bookings"
