from django.urls import path
from .views import *
urlpatterns = [
    path('',PaymentView.as_view()),
    path('particular/',ParticularPaymentView.as_view()),
    path('recents/',RecentPaymentHistory.as_view()),
    path('popular/',CategoryItemPopularityView.as_view()),
    path('history/<str:history_type>/', PaymentHistory.as_view(), name='payment_history'),
    path('order-distribution/<str:history_type>/', OrderTypeDistributionView.as_view(), name='payment_history'),
]
