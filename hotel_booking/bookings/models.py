from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator, validate_email
from django.utils import timezone
from core.models import Hotel, Room
from django.core.exceptions import ValidationError
import random
import string

User = get_user_model()


class Booking(models.Model):
    """
    Production-grade booking model with optimistic locking and comprehensive indexing.
    Supports high-concurrency scenarios with hundreds of simultaneous users.
    """
    
    # Status choices
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
    ]
    
    # Core booking information
    booking_id = models.CharField(
        max_length=30, 
        unique=True, 
        editable=False,
        help_text="Unique booking reference"
    )
    
    # Guest information
    guest_first_name = models.CharField(max_length=50)
    guest_last_name = models.CharField(max_length=50)
    guest_email = models.EmailField(validators=[validate_email])
    guest_phone = models.CharField(max_length=30)
    
    # Address information
    guest_country = models.CharField(max_length=100)
    guest_address = models.TextField()
    guest_city = models.CharField(max_length=100)
    guest_postal_code = models.CharField(max_length=20)
    
    # Optional passport information
    guest_passport_number = models.CharField(max_length=40, blank=True, null=True)
    
    # Booking details
    hotel = models.ForeignKey(
        Hotel, 
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    room = models.ForeignKey(
        Room, 
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    
    # Date and time information
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    check_in_time = models.TimeField(null=True,blank=True, help_text="Check-in time (default 3:00 PM)")
    check_out_time = models.TimeField(null=True,blank=True, help_text="Check-out time (default 11:00 AM)")
    nights = models.PositiveIntegerField(editable=False)
    
    # Guest count
    adults = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    children = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    
    # Pricing breakdown
    room_rate = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Rate per night before taxes"
    )
    subtotal = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        editable=False,
        help_text="Room rate × nights"
    )
    tax_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        default=0.00,
        help_text="VAT and municipality tax"
    )
    discount_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        default=0.00,
        help_text="Member discount or promotional discount"
    )
    total_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        editable=False,
        help_text="Final amount after taxes and discounts"
    )
    
    # Discount information
    discount_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="e.g., 'Member Discount', 'Summer Deal'"
    )
    
    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )
    
    # Optional notes
    special_requests = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Optimistic locking for concurrent updates
    version = models.IntegerField(default=0, help_text="Version counter for optimistic locking")
    
    # User association (optional for registered users)
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='bookings'
    )
    
    class Meta:
        db_table = 'booking'
        ordering = ['-created_at']
        # Comprehensive indexes for high-concurrency production environment
        indexes = [
            # Primary lookup indexes
            models.Index(fields=['booking_id'], name='idx_booking_id'),
            
            # Availability check indexes (critical for concurrency)
            models.Index(fields=['room', 'status', 'check_in_date', 'check_out_date'], 
                        name='idx_room_availability'),
            models.Index(fields=['room', 'check_in_date', 'check_out_date'], 
                        name='idx_room_dates'),
            
            # Hotel & Status indexes
            models.Index(fields=['hotel', 'status'], name='idx_hotel_status'),
            models.Index(fields=['hotel', 'created_at'], name='idx_hotel_created'),
            
            # User related indexes
            models.Index(fields=['user', 'status'], name='idx_user_status'),
            models.Index(fields=['user', 'created_at'], name='idx_user_created'),
            
            # Guest lookup indexes
            models.Index(fields=['guest_email'], name='idx_guest_email'),
            models.Index(fields=['guest_phone'], name='idx_guest_phone'),
            
            # Date range indexes for reporting
            models.Index(fields=['check_in_date'], name='idx_checkin'),
            models.Index(fields=['check_out_date'], name='idx_checkout'),
            models.Index(fields=['created_at'], name='idx_created'),
            
            # Payment tracking indexes
            models.Index(fields=['payment_status', 'created_at'], name='idx_payment_created'),
            
            # Status tracking for automation
            models.Index(fields=['status', 'created_at'], name='idx_status_created'),
        ]
    
    def save(self, *args, **kwargs):
        # Generate booking ID if not exists
        if not self.booking_id:
            self.booking_id = self.generate_booking_id()
        
        # Calculate nights
        if self.check_in_date and self.check_out_date:
            self.nights = (self.check_out_date - self.check_in_date).days
        
        # Calculate pricing breakdown
        if self.room_rate and self.nights:
            # Calculate subtotal (room rate × nights)
            self.subtotal = self.room_rate * self.nights
            
            # Calculate total with taxes and discounts
            total_before_tax = self.subtotal - self.discount_amount
            self.total_amount = total_before_tax + self.tax_amount
        
        # Validate before saving
        self.clean()
        super().save(*args, **kwargs)
    
    def generate_booking_id(self):
        """Generate a unique booking ID"""
        while True:
            booking_id = 'BK' + ''.join(random.choices(string.digits, k=8))
            if not Booking.objects.filter(booking_id=booking_id).exists():
                return booking_id
    
    def clean(self):
        """Validate booking data"""
        errors = {}
        
        # Check dates
        if self.check_in_date and self.check_out_date:
            if self.check_in_date >= self.check_out_date:
                errors['check_out_date'] = 'Check-out date must be after check-in date'
            
            if self.check_in_date < timezone.now().date():
                errors['check_in_date'] = 'Check-in date cannot be in the past'
        
        # Check room capacity
        if self.room and (self.adults + self.children) > self.room.capacity:
            errors['adults'] = f'Total guests exceed room capacity ({self.room.capacity})'
        
        if errors:
            raise ValidationError(errors)
    
    def can_be_cancelled(self):
        """Check if booking can be cancelled"""
        if self.status in ['cancelled', 'completed']:
            return False
        return self.check_in_date > timezone.now().date()
    
    def guest_full_name(self):
        """Return guest's full name"""
        return f"{self.guest_first_name} {self.guest_last_name}"
    
    def guest_address_formatted(self):
        """Return formatted address"""
        return f"{self.guest_address}, {self.guest_city}, {self.guest_postal_code}, {self.guest_country}"
    
    def tax_percentage(self):
        """Calculate tax percentage for display"""
        if self.subtotal > 0:
            return round((self.tax_amount / self.subtotal) * 100, 1)
        return 0
    
    def discount_percentage(self):
        """Calculate discount percentage for display"""
        if self.subtotal > 0:
            return round((self.discount_amount / self.subtotal) * 100, 1)
        return 0
    
    def total_guests(self):
        """Return total number of guests"""
        return self.adults + self.children
    
    def __str__(self):
        return f"{self.booking_id} - {self.guest_full_name()} ({self.hotel.name})"
