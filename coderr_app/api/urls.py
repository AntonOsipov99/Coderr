from django.urls import path
from .views import OfferView, OfferViewDetail, ReviewList, OrdersView, OrderCountView, CompletedOrderCountView, BaseInfoView

urlpatterns = [
    path('reviews/', ReviewList.as_view(), name='review-list'),
    path('orders/', OrdersView.as_view(), name='order-list'),
    path('order-count/', OrderCountView.as_view(), name='order-count'),
    path('completed-order-count/', CompletedOrderCountView.as_view(), name='completed-order-count'),
    path('offers/', OfferView.as_view(), name='offer-list'),
    path('offerdetails/<int:pk>/', OfferViewDetail.as_view(), name='offer-detail-list'),
    path('base-info/', BaseInfoView.as_view(), name='base-info'),
]