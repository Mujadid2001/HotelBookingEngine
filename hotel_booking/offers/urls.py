# Django imports
from django.urls import path, include

# Local imports
from .views import (
    OfferListCreateView, OfferDetailView, FeaturedOffersView,
    OfferSearchView, OfferCalculationView,
    OfferHighlightListCreateView, OfferHighlightDetailView,
    OfferImageListCreateView, OfferImageDetailView,
    OfferCategoryListCreateView, OfferCategoryDetailView, OffersByCategoryView
)

app_name = 'offers'

urlpatterns = [
    # Category endpoints
    path('categories/', OfferCategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<slug:slug>/', OfferCategoryDetailView.as_view(), name='category-detail'),
    path('by-category/', OffersByCategoryView.as_view(), name='offers-by-category'),
    
    # Special offer endpoints (place before slug-based endpoints to avoid conflicts)
    path('featured/', FeaturedOffersView.as_view(), name='featured-offers'),
    path('search/', OfferSearchView.as_view(), name='offer-search'),
    path('calculate/', OfferCalculationView.as_view(), name='offer-calculation'),
    
    # Main offer endpoints
    path('', OfferListCreateView.as_view(), name='offer-list-create'),
    path('<slug:slug>/', OfferDetailView.as_view(), name='offer-detail'),
    
    # Offer highlights endpoints
    path('<uuid:offer_id>/highlights/', OfferHighlightListCreateView.as_view(), name='offer-highlights-list-create'),
    path('<uuid:offer_id>/highlights/<int:pk>/', OfferHighlightDetailView.as_view(), name='offer-highlight-detail'),
    
    # Offer images endpoints
    path('<uuid:offer_id>/images/', OfferImageListCreateView.as_view(), name='offer-images-list-create'),
    path('<uuid:offer_id>/images/<int:pk>/', OfferImageDetailView.as_view(), name='offer-image-detail'),
]
