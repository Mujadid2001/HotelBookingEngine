# Django imports
from django.db import models
from django.conf import settings

# Local imports
from core.models import Room, Extra


class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    check_in = models.DateField()
    check_out = models.DateField()
    guests = models.PositiveIntegerField()
    extras = models.ManyToManyField(Extra, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def calculate_price(self):
        nights = (self.check_out - self.check_in).days
        room_price = self.room.price_per_night * nights
        extras_price = sum(extra.price for extra in self.extras.all())
        return room_price + extras_price

    def save(self, *args, **kwargs):
        self.total_price = self.calculate_price()
        super().save(*args, **kwargs)
