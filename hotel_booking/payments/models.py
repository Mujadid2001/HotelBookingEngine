"""Payment models for Tap Payments integration"""
from django.db import models
from bookings.models import Booking


class Payment(models.Model):
    """Payment transactions for bookings"""
    PAYMENT_METHOD_CHOICES = [
        ('tap', 'Tap Payments'),
        ('bank_transfer', 'Bank Transfer'),
        ('on_arrival', 'Pay on Arrival'),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Amount in currency")
    currency = models.CharField(max_length=3, default='SAR', help_text="ISO 4217 currency code")
    method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='tap')
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending', db_index=True)
    transaction_id = models.CharField(max_length=100, blank=True, null=True, unique=True, help_text="External provider transaction ID")
    idempotency_key = models.CharField(max_length=100, blank=True, null=True, unique=True, help_text="Unique request key")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payment'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['booking'], name='idx_payment_booking'),
            models.Index(fields=['status', 'created_at'], name='idx_payment_status_created'),
            models.Index(fields=['transaction_id'], name='idx_payment_transaction'),
        ]
    
    def __str__(self):
        return f"Payment {self.id}: {self.booking.booking_id} - {self.amount} {self.currency}"


class TapPaymentTransaction(models.Model):
    """Tap-specific payment transaction details"""
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='tap_transaction')
    tap_id = models.CharField(max_length=100, unique=True, help_text="Tap charge ID")
    tap_source_id = models.CharField(max_length=100, blank=True, null=True, help_text="Tap source/card ID")
    tap_card_last_4 = models.CharField(max_length=4, blank=True, null=True)
    tap_card_brand = models.CharField(max_length=50, blank=True, null=True)
    tap_success = models.BooleanField(default=False)
    tap_response_code = models.CharField(max_length=10, blank=True, null=True)
    tap_error_message = models.TextField(blank=True, null=True)
    tap_raw_response = models.JSONField(default=dict, blank=True, help_text="Full Tap API response")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tap_payment_transaction'
        ordering = ['-created_at']
        indexes = [models.Index(fields=['tap_id'], name='idx_tap_id')]
    
    def __str__(self):
        status = "✓" if self.tap_success else "✗"
        return f"Tap {self.tap_id}: {status}"
