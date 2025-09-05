# Django imports
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import date, timedelta

# Django REST Framework imports
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

# Local imports
from .models import Offer, OfferHighlight, OfferImage
from core.models import Hotel, RoomType
from accounts.models import CustomUser


class OfferModelTest(TestCase):
    """Test cases for Offer model"""
    
    def setUp(self):
        """Set up test data"""
        self.hotel = Hotel.objects.create(
            name="Test Hotel",
            email="test@hotel.com",
            address_line_1="123 Test St"
        )
        
        self.room_type = RoomType.objects.create(
            name="Standard Room",
            hotel=self.hotel,
            base_price=Decimal('100.00'),
            capacity=2
        )
        
        self.offer_data = {
            'name': 'Summer Special',
            'description': 'Great summer offer',
            'offer_type': 'percentage',
            'discount_percentage': Decimal('20.00'),
            'valid_from': date.today(),
            'valid_to': date.today() + timedelta(days=30),
            'hotel': self.hotel,
            'minimum_stay': 2
        }
    
    def test_offer_creation(self):
        """Test creating a valid offer"""
        offer = Offer.objects.create(**self.offer_data)
        self.assertEqual(offer.name, 'Summer Special')
        self.assertTrue(offer.is_valid)
        self.assertTrue(offer.is_available)
        self.assertIsNotNone(offer.slug)
    
    def test_offer_slug_generation(self):
        """Test automatic slug generation"""
        offer = Offer.objects.create(**self.offer_data)
        self.assertEqual(offer.slug, 'summer-special')
        
        # Test duplicate slug handling
        offer_data_2 = self.offer_data.copy()
        offer_data_2['name'] = 'Summer Special'
        offer2 = Offer.objects.create(**offer_data_2)
        self.assertEqual(offer2.slug, 'summer-special-1')
    
    def test_offer_validation(self):
        """Test offer validation"""
        # Test invalid date range
        invalid_data = self.offer_data.copy()
        invalid_data['valid_to'] = date.today() - timedelta(days=1)
        
        offer = Offer(**invalid_data)
        with self.assertRaises(ValidationError):
            offer.clean()
    
    def test_discount_calculation(self):
        """Test discount calculation"""
        offer = Offer.objects.create(**self.offer_data)
        base_price = Decimal('100.00')
        nights = 3
        
        # Test percentage discount
        discount = offer.calculate_discount(base_price, nights)
        expected = base_price * nights * Decimal('0.20')  # 20% off total
        self.assertEqual(discount, expected)
    
    def test_applies_to_date(self):
        """Test date applicability"""
        offer = Offer.objects.create(**self.offer_data)
        
        # Test valid date
        test_date = date.today() + timedelta(days=1)
        self.assertTrue(offer.applies_to_date(test_date))
        
        # Test invalid date (past valid_to)
        test_date = date.today() + timedelta(days=40)
        self.assertFalse(offer.applies_to_date(test_date))
    
    def test_offer_availability(self):
        """Test offer availability limits"""
        offer_data = self.offer_data.copy()
        offer_data['total_bookings_limit'] = 5
        offer_data['bookings_used'] = 4
        
        offer = Offer.objects.create(**offer_data)
        self.assertTrue(offer.is_available)
        
        # Exceed limit
        offer.bookings_used = 5
        offer.save()
        self.assertFalse(offer.is_available)


class OfferHighlightModelTest(TestCase):
    """Test cases for OfferHighlight model"""
    
    def setUp(self):
        """Set up test data"""
        self.hotel = Hotel.objects.create(
            name="Test Hotel",
            email="test@hotel.com",
            address_line_1="123 Test St"
        )
        
        self.offer = Offer.objects.create(
            name='Test Offer',
            description='Test description',
            offer_type='percentage',
            discount_percentage=Decimal('15.00'),
            valid_from=date.today(),
            valid_to=date.today() + timedelta(days=30),
            hotel=self.hotel
        )
    
    def test_highlight_creation(self):
        """Test creating offer highlights"""
        highlight = OfferHighlight.objects.create(
            offer=self.offer,
            title='Free Breakfast',
            description='Complimentary breakfast included',
            order=1
        )
        
        self.assertEqual(highlight.title, 'Free Breakfast')
        self.assertEqual(highlight.order, 1)
        self.assertEqual(str(highlight), 'Test Offer - Free Breakfast')


class OfferAPITest(APITestCase):
    """Test cases for Offer API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create test user
        self.user = CustomUser.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Create test hotel
        self.hotel = Hotel.objects.create(
            name="Test Hotel",
            email="test@hotel.com",
            address_line_1="123 Test St"
        )
        
        # Create test room type
        self.room_type = RoomType.objects.create(
            name="Standard Room",
            hotel=self.hotel,
            base_price=Decimal('100.00'),
            capacity=2
        )
        
        # Create test offer
        self.offer = Offer.objects.create(
            name='Test Offer',
            description='Test description',
            offer_type='percentage',
            discount_percentage=Decimal('20.00'),
            valid_from=date.today(),
            valid_to=date.today() + timedelta(days=30),
            hotel=self.hotel,
            minimum_stay=1,
            is_featured=True
        )
        
        # Add highlights and images
        self.highlight = OfferHighlight.objects.create(
            offer=self.offer,
            title='Free Breakfast',
            description='Complimentary breakfast',
            order=1
        )
    
    def get_jwt_token(self):
        """Get JWT token for authentication"""
        refresh = RefreshToken.for_user(self.user)
        return str(refresh.access_token)
    
    def test_offer_list(self):
        """Test listing offers"""
        url = reverse('offers:offer-list-create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['name'], 'Test Offer')
    
    def test_offer_detail(self):
        """Test getting offer details"""
        url = reverse('offers:offer-detail', kwargs={'slug': self.offer.slug})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Offer')
        self.assertEqual(len(response.data['highlights']), 1)
    
    def test_featured_offers(self):
        """Test getting featured offers"""
        url = reverse('offers:featured-offers')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertTrue(response.data[0]['is_featured'])
    
    def test_offer_search(self):
        """Test offer search"""
        url = reverse('offers:offer-search')
        data = {
            'hotel_id': str(self.hotel.id),
            'offer_type': 'percentage'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
    
    def test_offer_calculation(self):
        """Test offer discount calculation"""
        url = reverse('offers:offer-calculation')
        data = {
            'offer_id': str(self.offer.id),
            'base_price': '100.00',
            'nights': 3,
            'check_in': str(date.today()),
            'check_out': str(date.today() + timedelta(days=3))
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_applicable'])
        self.assertEqual(response.data['discount_amount'], '60.00')  # 20% of 300
    
    def test_offer_creation_requires_auth(self):
        """Test that creating offers requires authentication"""
        url = reverse('offers:offer-list-create')
        data = {
            'name': 'New Offer',
            'description': 'Test offer',
            'offer_type': 'percentage',
            'discount_percentage': '15.00',
            'valid_from': str(date.today()),
            'valid_to': str(date.today() + timedelta(days=30)),
            'hotel': str(self.hotel.id)
        }
        
        # Without authentication
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # With authentication
        token = self.get_jwt_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_offer_filtering(self):
        """Test offer filtering"""
        # Create another offer with different type
        Offer.objects.create(
            name='Package Deal',
            description='Package description',
            offer_type='package',
            package_price=Decimal('250.00'),
            valid_from=date.today(),
            valid_to=date.today() + timedelta(days=30),
            hotel=self.hotel
        )
        
        url = reverse('offers:offer-list-create')
        
        # Filter by offer type
        response = self.client.get(url, {'offer_type': 'percentage'})
        self.assertEqual(response.data['count'], 1)
        
        # Filter by hotel
        response = self.client.get(url, {'hotel_id': str(self.hotel.id)})
        self.assertEqual(response.data['count'], 2)
        
        # Filter by featured
        response = self.client.get(url, {'is_featured': 'true'})
        self.assertEqual(response.data['count'], 1)
    
    def test_offer_highlights_api(self):
        """Test offer highlights API"""
        url = reverse('offers:offer-highlights-list-create', kwargs={'offer_id': self.offer.id})
        
        # List highlights
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # Create new highlight (requires auth)
        token = self.get_jwt_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        data = {
            'title': 'Free WiFi',
            'description': 'High-speed internet',
            'order': 2
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class OfferManagerTest(TestCase):
    """Test cases for Offer manager methods"""
    
    def setUp(self):
        """Set up test data"""
        self.hotel = Hotel.objects.create(
            name="Test Hotel",
            email="test@hotel.com",
            address_line_1="123 Test St"
        )
        
        # Create active offer
        self.active_offer = Offer.objects.create(
            name='Active Offer',
            description='Active description',
            offer_type='percentage',
            discount_percentage=Decimal('15.00'),
            valid_from=date.today() - timedelta(days=5),
            valid_to=date.today() + timedelta(days=25),
            hotel=self.hotel,
            is_active=True
        )
        
        # Create inactive offer
        self.inactive_offer = Offer.objects.create(
            name='Inactive Offer',
            description='Inactive description',
            offer_type='percentage',
            discount_percentage=Decimal('10.00'),
            valid_from=date.today(),
            valid_to=date.today() + timedelta(days=30),
            hotel=self.hotel,
            is_active=False
        )
        
        # Create expired offer
        self.expired_offer = Offer.objects.create(
            name='Expired Offer',
            description='Expired description',
            offer_type='percentage',
            discount_percentage=Decimal('25.00'),
            valid_from=date.today() - timedelta(days=30),
            valid_to=date.today() - timedelta(days=1),
            hotel=self.hotel,
            is_active=True
        )
        
        # Create featured offer
        self.featured_offer = Offer.objects.create(
            name='Featured Offer',
            description='Featured description',
            offer_type='percentage',
            discount_percentage=Decimal('30.00'),
            valid_from=date.today(),
            valid_to=date.today() + timedelta(days=30),
            hotel=self.hotel,
            is_active=True,
            is_featured=True
        )
    
    def test_active_offers_manager(self):
        """Test active offers manager method"""
        active_offers = Offer.objects.active_offers()
        
        # Should include active and featured offers, exclude inactive and expired
        self.assertIn(self.active_offer, active_offers)
        self.assertIn(self.featured_offer, active_offers)
        self.assertNotIn(self.inactive_offer, active_offers)
        self.assertNotIn(self.expired_offer, active_offers)
    
    def test_for_hotel_manager(self):
        """Test for_hotel manager method"""
        hotel_offers = Offer.objects.for_hotel(self.hotel)
        self.assertEqual(hotel_offers.count(), 4)
    
    def test_featured_offers_manager(self):
        """Test featured offers manager method"""
        featured_offers = Offer.objects.featured_offers()
        
        # Should only include featured offer that is also active and valid
        self.assertEqual(featured_offers.count(), 1)
        self.assertIn(self.featured_offer, featured_offers)
    
    def test_for_date_range_manager(self):
        """Test for_date_range manager method"""
        start_date = date.today()
        end_date = date.today() + timedelta(days=10)
        
        date_range_offers = Offer.objects.for_date_range(start_date, end_date)
        
        # Should include offers that overlap with the date range
        self.assertIn(self.active_offer, date_range_offers)
        self.assertIn(self.featured_offer, date_range_offers)
        self.assertNotIn(self.expired_offer, date_range_offers)
