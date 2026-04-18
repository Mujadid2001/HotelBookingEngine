"""Payment API URLs"""
from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('', views.PaymentListView.as_view(), name='payment-list'),
    path('initiate/', views.InitiatePaymentView.as_view(), name='payment-initiate'),
    path('<int:pk>/', views.PaymentStatusView.as_view(), name='payment-detail'),
    path('<int:pk>/refund/', views.PaymentRefundView.as_view(), name='payment-refund'),
    path('callback/', views.TapPaymentCallbackView.as_view(), name='payment-callback'),
]
