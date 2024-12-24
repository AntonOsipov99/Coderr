from rest_framework.authtoken.models import Token
from rest_framework import generics
from user_auth_app.models import UserProfile
from .serializers import UserProfileSerializer, RegistrationSerializer
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken

class UserProfileList(generics.ListCreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

class UserProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    
class BusinessProfileList(generics.ListCreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    
class CustomerProfileList(generics.ListCreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    
    
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
        
        data = {}
        if serializer.is_valid():
            save_account = serializer.save()
            token, created = Token.objects.get_or_create(user=save_account)
            profile = UserProfile.objects.get(user=save_account)
            data = {
                'token': token.key,
                'username': save_account.username,
                'email': save_account.email,
                'user_id': save_account.id,
            }
            return Response(data)
        
        return Response(serializer.errors)