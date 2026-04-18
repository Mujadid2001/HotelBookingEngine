"""Payments app admin configuration"""
from django.contrib import admin
from .models import Payment, TapPaymentTransaction


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Payment model admin"""
    list_display = ('id', 'booking', 'amount', 'currency', 'method', 'status', 'transaction_id', 'created_at')
    list_filter = ('status', 'method', 'currency', 'created_at')
    search_fields = ('transaction_id', 'booking__booking_id', 'booking__guest_email')
    readonly_fields = ('transaction_id', 'idempotency_key', 'created_at', 'updated_at')
    fieldsets = (
        ('Booking', {'fields': ('booking',)}),
        ('Payment Details', {'fields': ('amount', 'currency', 'method', 'status')}),
        ('Transaction', {'fields': ('transaction_id', 'idempotency_key')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    ordering = ('-created_at',)


@admin.register(TapPaymentTransaction)
class TapPaymentTransactionAdmin(admin.ModelAdmin):
    """Tap payment transaction admin"""
    list_display = ('tap_id', 'payment', 'tap_success', 'tap_response_code', 'created_at')
    list_filter = ('tap_success', 'tap_response_code', 'created_at')
    search_fields = ('tap_id', 'tap_source_id', 'payment__booking__booking_id')
    readonly_fields = ('tap_id', 'tap_raw_response', 'created_at', 'updated_at')
    fieldsets = (
        ('Tap Details', {'fields': ('tap_id', 'tap_source_id', 'tap_success')}),
        ('Card Info', {'fields': ('tap_card_last_4', 'tap_card_brand')}),
        ('Response', {'fields': ('tap_response_code', 'tap_error_message', 'tap_raw_response')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    ordering = ('-created_at',)
