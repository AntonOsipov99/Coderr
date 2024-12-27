from rest_framework.authtoken.models import Token
from rest_framework import generics
from .serializers import  BusinessProfileSerializer, ProfileSerializer, CustomerProfileSerializer, RegistrationSerializer
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from user_auth_app.models import BusinessPartner, Customer
from rest_framework import status
from coderr_app.api.permissions import IsOwnerOrAdmin

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk is None:
            pk = request.user.id

        business_profile = BusinessPartner.objects.filter(user__id=pk).first()
        if business_profile:
            serializer = ProfileSerializer(business_profile)
            return Response(serializer.data, status=status.HTTP_200_OK)

        customer_profile = Customer.objects.filter(user__id=pk).first()
        if customer_profile:
            serializer = CustomerProfileSerializer(customer_profile)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(
            {"error": "Profil nicht gefunden"}, 
            status=status.HTTP_404_NOT_FOUND
        )

    def patch(self, request, pk=None):
        # Wenn keine pk angegeben ist, nutze die ID des eingeloggten Users
        if pk is None:
            pk = request.user.id

        # Überprüfe, ob der User sein eigenes Profil bearbeitet
        if request.user.id != pk:
            return Response(
                {"error": "Sie können nur Ihr eigenes Profil bearbeiten"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Finde das entsprechende Profil
        business_profile = BusinessPartner.objects.filter(user__id=pk).first()
        customer_profile = Customer.objects.filter(user__id=pk).first()
        profile = business_profile or customer_profile

        if not profile:
            return Response(
                {"error": "Profil nicht gefunden"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Update des Profils
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            # Update User model fields
            user = profile.user
            if 'first_name' in request.data:
                user.first_name = request.data['first_name']
            if 'last_name' in request.data:
                user.last_name = request.data['last_name']
            user.save()

            # Update profile fields
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class BusinessProfileList(generics.ListAPIView):
    queryset = BusinessPartner.objects.all()
    serializer_class = BusinessProfileSerializer
    
class CustomerProfileList(generics.ListAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerProfileSerializer
    
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

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                save_account = serializer.save()
                token, created = Token.objects.get_or_create(user=save_account)
                type = serializer.validated_data['type']
                if type == 'business':
                    profile = BusinessPartner.objects.get(user=save_account)
                else:
                    profile = Customer.objects.get(user=save_account)

                data = {
                    'token': token.key,
                    'username': save_account.username,
                    'email': save_account.email,
                    'user_id': save_account.id,
                    'type': type
                }
                return Response(data, status=status.HTTP_201_CREATED)
            
            except Exception as e:
                save_account.delete()
                return Response({
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)