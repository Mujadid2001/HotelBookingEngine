"""Payment signal handlers - email notifications"""
from django.dispatch import Signal
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Custom signals for payment events
payment_successful = Signal()
payment_failed = Signal()
payment_refunded = Signal()


@receiver(payment_successful)
def on_payment_successful(sender, payment, booking, **kwargs):
    """Email notification on successful payment"""
    try:
        subject = f'Payment Confirmed - {booking.booking_id}'
        message = f"""Dear {booking.guest_full_name()},

Your payment of {payment.amount} {payment.currency} has been successfully confirmed!

Booking Details:
- Reference: {booking.booking_id}
- Transaction ID: {payment.transaction_id}
- Hotel: {booking.hotel.name}
- Check-in: {booking.check_in_date}
- Check-out: {booking.check_out_date}
- Total Amount: {booking.total_amount} SAR

Your booking is now confirmed. We look forward to your stay!

Best regards,
Hotel Booking Team"""
        
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [booking.guest_email], fail_silently=True)
        logger.info(f"Payment success email sent: {booking.booking_id}")
    except Exception as e:
        logger.error(f"Payment success email error: {str(e)}")


@receiver(payment_failed)
def on_payment_failed(sender, payment, error_message=None, **kwargs):
    """Email notification on payment failure"""
    try:
        subject = f'Payment Failed - {payment.booking.booking_id}'
        message = f"""Dear {payment.booking.guest_full_name()},

Unfortunately, your payment attempt failed.

Booking Reference: {payment.booking.booking_id}
Error: {error_message or 'Unknown error'}

Please try again with a different card or payment method. 
Contact support if you need assistance.

Best regards,
Hotel Booking Team"""
        
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [payment.booking.guest_email], fail_silently=True)
        logger.info(f"Payment failure email sent: {payment.booking.booking_id}")
    except Exception as e:
        logger.error(f"Payment failure email error: {str(e)}")


@receiver(payment_refunded)
def on_payment_refunded(sender, payment, booking, **kwargs):
    """Email notification on refund processing"""
    try:
        subject = f'Refund Processed - {booking.booking_id}'
        message = f"""Dear {booking.guest_full_name()},

Your refund has been processed successfully!

Refund Details:
- Booking Reference: {booking.booking_id}
- Refund Amount: {payment.amount} {payment.currency}
- Transaction ID: {payment.transaction_id}

The funds should appear back in your original payment method within 3-5 business days.

Thank you for choosing us!

Best regards,
Hotel Booking Team"""
        
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [booking.guest_email], fail_silently=True)
        logger.info(f"Refund notification email sent: {booking.booking_id}")
    except Exception as e:
        logger.error(f"Refund email error: {str(e)}")
