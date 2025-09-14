from django.contrib import admin
from django.utils.html import format_html
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """Clean admin interface for simplified booking model"""
    
    list_display = [
        'booking_id', 'guest_full_name_display', 'hotel_name', 'room_info',
        'check_in_date', 'check_out_date', 'nights', 'total_guests_display',
        'status_badge', 'payment_status_badge', 'total_amount', 'created_at'
    ]
    
    list_filter = [
        'status', 'payment_status', 'hotel', 'guest_country', 'check_in_date', 'created_at'
    ]
    
    search_fields = [
        'booking_id', 'guest_first_name', 'guest_last_name', 'guest_email', 
        'guest_phone', 'hotel__name', 'room__room_number'
    ]
    
    readonly_fields = [
        'booking_id', 'nights', 'subtotal', 'total_amount', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('booking_id', 'status', 'payment_status', 'created_at', 'updated_at')
        }),
        ('Guest Details', {
            'fields': (
                ('guest_first_name', 'guest_last_name'), 
                'guest_email', 'guest_phone', 'guest_passport_number', 'user'
            )
        }),
        ('Address Information', {
            'fields': ('guest_address', ('guest_city', 'guest_postal_code'), 'guest_country'),
            'classes': ('collapse',)
        }),
        ('Booking Details', {
            'fields': (
                'hotel', 'room', 
                ('check_in_date', 'check_in_time'), 
                ('check_out_date', 'check_out_time'), 
                'nights'
            )
        }),
        ('Guest Count', {
            'fields': ('adults', 'children')
        }),
        ('Pricing', {
            'fields': (
                'room_rate', 'subtotal', 'tax_amount', 
                ('discount_amount', 'discount_type'), 'total_amount'
            )
        }),
        ('Additional Information', {
            'fields': ('special_requests',),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    def guest_full_name_display(self, obj):
        """Display guest full name"""
        return obj.guest_full_name()
    guest_full_name_display.short_description = 'Guest Name'
    
    def hotel_name(self, obj):
        """Display hotel name"""
        return obj.hotel.name if obj.hotel else '-'
    hotel_name.short_description = 'Hotel'
    
    def room_info(self, obj):
        """Display room information"""
        if obj.room:
            return f"{obj.room.room_number} ({obj.room.room_type.name})"
        return '-'
    room_info.short_description = 'Room'
    
    def total_guests_display(self, obj):
        """Display total guests count"""
        return f"{obj.adults} adults" + (f", {obj.children} children" if obj.children > 0 else "")
    total_guests_display.short_description = 'Guests'
    
    def status_badge(self, obj):
        """Display status with color badge"""
        colors = {
            'pending': '#ffc107',    # yellow
            'confirmed': '#28a745',   # green
            'cancelled': '#dc3545',   # red
            'completed': '#6c757d',   # gray
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def payment_status_badge(self, obj):
        """Display payment status with color badge"""
        colors = {
            'pending': '#ffc107',    # yellow
            'paid': '#28a745',       # green
            'refunded': '#17a2b8',   # blue
        }
        color = colors.get(obj.payment_status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px;">{}</span>',
            color, obj.get_payment_status_display()
        )
    payment_status_badge.short_description = 'Payment'
    
    def get_queryset(self, request):
        """Optimize queries"""
        return super().get_queryset(request).select_related(
            'hotel', 'room', 'room__room_type', 'user'
        )
    
    actions = ['mark_confirmed', 'mark_cancelled', 'mark_paid']
    
    def mark_confirmed(self, request, queryset):
        """Mark selected bookings as confirmed"""
        updated = queryset.filter(status='pending').update(status='confirmed')
        self.message_user(request, f'{updated} bookings marked as confirmed.')
    mark_confirmed.short_description = 'Mark selected bookings as confirmed'
    
    def mark_cancelled(self, request, queryset):
        """Mark selected bookings as cancelled"""
        updated = queryset.exclude(status__in=['cancelled', 'completed']).update(status='cancelled')
        self.message_user(request, f'{updated} bookings marked as cancelled.')
    mark_cancelled.short_description = 'Mark selected bookings as cancelled'
    
    def mark_paid(self, request, queryset):
        """Mark selected bookings as paid"""
        updated = queryset.filter(payment_status='pending').update(payment_status='paid')
        self.message_user(request, f'{updated} bookings marked as paid.')
    mark_paid.short_description = 'Mark selected bookings as paid'
