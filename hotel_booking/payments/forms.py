"""Payment forms"""
from django import forms
from django.core.exceptions import ValidationError


class PaymentMethodForm(forms.Form):
    """Form to select payment method"""
    PAYMENT_METHOD_CHOICES = [
        ('tap', 'Pay with Card (Tap Payments)'),
        ('bank_transfer', 'Bank Transfer'),
        ('on_arrival', 'Pay on Arrival'),
    ]
    
    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHOD_CHOICES,
        widget=forms.RadioSelect,
        label='Payment Method',
        help_text='Choose your preferred payment method'
    )


class TapCardPaymentForm(forms.Form):
    """Form for Tap card payment details"""
    cardholder_name = forms.CharField(
        max_length=100,
        required=True,
        label='Cardholder Name',
        widget=forms.TextInput(attrs={'placeholder': 'Full Name', 'class': 'form-control'})
    )
    cardholder_email = forms.EmailField(
        required=True,
        label='Email Address',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    tap_source_id = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.HiddenInput(),
        label='Card Token'
    )
    card_last_4 = forms.CharField(
        max_length=4,
        required=False,
        label='Last 4 Digits',
        widget=forms.TextInput(attrs={'readonly': True, 'class': 'form-control'})
    )
    card_brand = forms.CharField(
        max_length=50,
        required=False,
        label='Card Brand',
        widget=forms.TextInput(attrs={'readonly': True, 'class': 'form-control'})
    )
    save_card = forms.BooleanField(
        required=False,
        label='Save card for future bookings',
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    agree_to_terms = forms.BooleanField(
        required=True,
        label='I agree to payment terms and conditions',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def clean_cardholder_name(self):
        name = self.cleaned_data.get('cardholder_name', '').strip()
        if not name or len(name) < 3:
            raise ValidationError('Please enter a valid cardholder name')
        return name
    
    def clean_tap_source_id(self):
        source_id = self.cleaned_data.get('tap_source_id', '').strip()
        if not source_id:
            raise ValidationError('Card tokenization failed. Please try again.')
        return source_id
    
    def clean_agree_to_terms(self):
        if not self.cleaned_data.get('agree_to_terms'):
            raise ValidationError('You must agree to the payment terms to proceed')
        return True
