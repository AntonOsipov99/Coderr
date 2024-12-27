from django.urls import include, path
from .views import OfferViewSet, OfferDetailViewSet, ReviewList, OrdersView, OrderCountView, CompletedOrderCountView, BaseInfoView, FileUploadView 
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'offers', OfferViewSet, basename='offers')
router.register(r'offerdetails', OfferDetailViewSet, basename='offerdetails')

urlpatterns = [
    path('', include(router.urls)),
    path('reviews/', ReviewList.as_view(), name='review-list'),
    path('orders/', OrdersView.as_view(), name='order-list'),
    path('order-count/', OrderCountView.as_view(), name='order-count'),
    path('completed-order-count/', CompletedOrderCountView.as_view(), name='completed-order-count'),
    # path('offers/', OffersView.as_view(), name='offers'),
    # path('offers/<int:pk>/', OfferViewDetail.as_view(), name='offer-detail'),
    # path('offerdetails/<int:pk>/', OffersViewDetail.as_view(), name='offer-detail-list'),
    path('base-info/', BaseInfoView.as_view(), name='base-info'),
    path('uploads/', FileUploadView.as_view(), name='file-upload'),
]