"""Payment serializers for REST API"""
from rest_framework import serializers
from django.utils.timesince import timesince
from .models import Payment, TapPaymentTransaction


class TapPaymentTransactionSerializer(serializers.ModelSerializer):
    """Tap transaction serializer (read-only for security)"""
    payment_amount = serializers.DecimalField(source='payment.amount', max_digits=10, decimal_places=2, read_only=True)
    payment_status = serializers.CharField(source='payment.status', read_only=True)
    
    class Meta:
        model = TapPaymentTransaction
        fields = ['id', 'tap_id', 'tap_card_last_4', 'tap_card_brand', 'tap_success', 'payment_amount', 'payment_status', 'created_at']
        read_only_fields = fields


class PaymentSerializer(serializers.ModelSerializer):
    """Payment serializer with related booking and Tap data"""
    booking_id = serializers.CharField(source='booking.booking_id', read_only=True)
    guest_name = serializers.SerializerMethodField(read_only=True)
    hotel_name = serializers.CharField(source='booking.hotel.name', read_only=True)
    tap_transaction = TapPaymentTransactionSerializer(read_only=True)
    time_since_created = serializers.SerializerMethodField(read_only=True)
    can_refund = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Payment
        fields = ['id', 'booking_id', 'guest_name', 'hotel_name', 'amount', 'currency', 'method', 'status', 'transaction_id', 'tap_transaction', 'time_since_created', 'can_refund', 'created_at', 'updated_at']
        read_only_fields = fields
    
    def get_guest_name(self, obj):
        return obj.booking.guest_full_name() if obj.booking else None
    
    def get_time_since_created(self, obj):
        return timesince(obj.created_at)
    
    def get_can_refund(self, obj):
        return obj.status == 'completed' and obj.booking.can_be_cancelled()


class PaymentListSerializer(serializers.ModelSerializer):
    """Simplified payment serializer for list endpoints"""
    booking_id = serializers.CharField(source='booking.booking_id', read_only=True)
    guest_name = serializers.SerializerMethodField(read_only=True)
    card_last_4 = serializers.CharField(source='tap_transaction.tap_card_last_4', read_only=True, allow_null=True)
    
    class Meta:
        model = Payment
        fields = ['id', 'booking_id', 'guest_name', 'amount', 'currency', 'method', 'status', 'card_last_4', 'created_at']
        read_only_fields = fields
    
    def get_guest_name(self, obj):
        return obj.booking.guest_full_name() if obj.booking else None
