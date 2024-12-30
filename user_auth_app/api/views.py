from rest_framework.authtoken.models import Token
from rest_framework import generics
from .serializers import BusinessProfileSerializer, BusinessSerializer, CustomerSerializer, CustomerProfileSerializer, RegistrationSerializer
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from user_auth_app.models import BusinessPartner, Customer
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from .utils import _check_user_permission, _update_user_data, _clean_profile_data, _handle_profile_update

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk=None):
        business_profile = BusinessPartner.objects.filter(user__id=pk).first()
        if business_profile:
            serializer = BusinessProfileSerializer(business_profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        customer_profile = Customer.objects.filter(user__id=pk).first()
        if customer_profile:
            serializer = CustomerProfileSerializer(customer_profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            {"error": "Profile not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )

    def patch(self, request, pk=None):
        permission_check = _check_user_permission(request.user.id, pk)
        if permission_check:
            return permission_check
        user = get_object_or_404(User, pk=pk)
        _update_user_data(user, request.data)
        profile_data = _clean_profile_data(request.data)
        business_profile = BusinessPartner.objects.filter(user=user).first()
        if business_profile:
            return _handle_profile_update(business_profile, BusinessProfileSerializer, profile_data)
        customer_profile = Customer.objects.filter(user=user).first()
        if customer_profile:
            return _handle_profile_update(customer_profile, CustomerProfileSerializer, profile_data)
        return Response(
            {"error": "Profile not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
class BusinessProfileList(generics.ListAPIView):
    queryset = BusinessPartner.objects.all()
    serializer_class = BusinessSerializer
    
class CustomerProfileList(generics.ListAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    
class CustomLoginView(ObtainAuthToken):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        data = {}
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            data = {
                'token': token.key,
                'username': user.username, 
                'email': user.email,
                'user_id': user.id
            }
        else:
            data = serializer.errors
        return Response(data)    
    
class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def prepare_registration_data(self, save_account, token, type):
        if type == 'business':
            profile = BusinessPartner.objects.get(user=save_account)
        else:
            profile = Customer.objects.get(user=save_account)
        return {
            'token': token.key,
            'username': save_account.username,
            'email': save_account.email,
            'user_id': save_account.id,
            'type': type
        }

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    
        try:
            save_account = serializer.save()
            token, created = Token.objects.get_or_create(user=save_account)
            type = serializer.validated_data['type']
            data = self.prepare_registration_data(save_account, token, type)
            return Response(data, status=status.HTTP_201_CREATED)
        except Exception as e:
            save_account.delete()
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)