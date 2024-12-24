
from rest_framework import serializers
from user_auth_app.models import UserProfile
from django.contrib.auth.models import User

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'
        
class RegistrationSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only= True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'repeated_password']
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }
        
    def save(self):
        pw = self.validated_data['password']
        repeated_pw = self.validated_data['repeated_password']
        # db_email = request.GET.get("email")
        
        if pw != repeated_pw:
            raise serializers.ValidationError({'error': 'passwords dont match'})
        
        # if db_email == self.validated_data['email']:
        #     raise serializers.ValidationError({'error':'Email exists already'})
        
        account = User(email=self.validated_data['email'], username=self.validated_data['username'])
        account.set_password(pw)
        account.save()
        return account