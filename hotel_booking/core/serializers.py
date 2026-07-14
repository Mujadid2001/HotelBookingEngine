from rest_framework import serializers
from .models import (
    ContactMessage, Hotel, Room, RoomType, Extra, SeasonalPricing,
    RoomImage, RoomAmenity, RoomTypeAmenity
)

__all__ = [
    'ContactMessageSerializer',
    'HotelSerializer',
    'RoomTypeSerializer',
    'RoomSerializer',
    'ExtraSerializer',
    'RoomAvailabilitySerializer',
    'RoomImageSerializer',
    'RoomAmenitySerializer',
    'RoomTypeAmenitySerializer',
    'SeasonalPricingSerializer',
]


class HotelSerializer(serializers.ModelSerializer):
    """Serializer for Hotel model"""
    
    class Meta:
        model = Hotel
        fields = '__all__'


class RoomImageSerializer(serializers.ModelSerializer):
    """Serializer for RoomImage model"""
    
    class Meta:
        model = RoomImage
        fields = '__all__'


class RoomAmenitySerializer(serializers.ModelSerializer):
    """Serializer for RoomAmenity model"""
    
    class Meta:
        model = RoomAmenity
        fields = '__all__'


class RoomTypeAmenitySerializer(serializers.ModelSerializer):
    """Serializer for RoomTypeAmenity model"""
    
    class Meta:
        model = RoomTypeAmenity
        fields = '__all__'


class SeasonalPricingSerializer(serializers.ModelSerializer):
    """Serializer for SeasonalPricing model"""
    
    class Meta:
        model = SeasonalPricing
        fields = '__all__'


class ContactMessageSerializer(serializers.ModelSerializer):
    """Serializer for ContactMessage model"""

    class Meta:
        model = ContactMessage
        fields = [
            'id',
            'full_name',
            'email',
            'phone',
            'subject',
            'message',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        """Create a new contact message"""
        return ContactMessage.objects.create(**validated_data)


class RoomTypeSerializer(serializers.ModelSerializer):
    """Serializer for RoomType model"""
    
    class Meta:
        model = RoomType
        fields = '__all__'


class RoomSerializer(serializers.ModelSerializer):
    """Serializer for Room model"""
    room_type_name = serializers.CharField(source='room_type.name', read_only=True)
    hotel_name = serializers.CharField(source='hotel.name', read_only=True)
    
    class Meta:
        model = Room
        fields = '__all__'


class ExtraSerializer(serializers.ModelSerializer):
    """Serializer for Extra model"""
    
    class Meta:
        model = Extra
        fields = '__all__'


class RoomAvailabilitySerializer(serializers.Serializer):
    """Serializer for room availability queries"""
    check_in_date = serializers.DateField()
    check_out_date = serializers.DateField()
    guests = serializers.IntegerField(min_value=1)
    room_type = serializers.UUIDField(required=False)
