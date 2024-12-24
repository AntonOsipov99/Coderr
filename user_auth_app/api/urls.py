from django.urls import path
from .views import BusinessProfileList, CustomerProfileList, UserProfileList, UserProfileDetail, RegistrationView, CustomLoginView
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('profile/', UserProfileList.as_view(), name='profile'),
    path('profile/<int:pk>/', UserProfileDetail.as_view(), name='profile'),
    path('profiles/business/', BusinessProfileList.as_view(), name='business-profiles'),
    path('profiles/customer/', CustomerProfileList.as_view(), name='customer-profiles'),
]