from django.urls import include, path
from .views import OfferViewSet, OfferDetailViewSet, OrdersViewSet, ReviewViewSet, BaseInfoView, FileUploadView
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'offers', OfferViewSet, basename='offers')
router.register(r'offerdetails', OfferDetailViewSet, basename='offerdetails')
router.register(r'orders', OrdersViewSet, basename='orders')
router.register(r'reviews', ReviewViewSet, basename='reviews')

urlpatterns = [
    path('', include(router.urls)),
    path('order-count/<int:business_user_id>/', views.get_order_count),
    path('completed-order-count/<int:business_user_id>/', views.get_completed_order_count),
    path('base-info/', BaseInfoView.as_view(), name='base-info'),
    path('uploads/', FileUploadView.as_view(), name='file-upload'),
]