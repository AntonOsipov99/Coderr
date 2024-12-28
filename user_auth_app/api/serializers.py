
from rest_framework import serializers
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from user_auth_app.models import BusinessPartner, Customer

# User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['pk', 'username', 'first_name', 'last_name']

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    file = serializers.FileField(required=False)
    location = serializers.CharField(required=False, allow_blank=True)
    tel = serializers.CharField(required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)
    working_hours = serializers.CharField(required=False, allow_blank=True)
    type = serializers.CharField(read_only=True)
    email = serializers.EmailField(required=False)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = BusinessPartner
        fields = ['user', 'file', 
                 'location', 'tel', 'description', 'working_hours', 
                 'type', 'email', 'created_at']
class CustomerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    
    class Meta:
        model = Customer
        fields = [
            'user',
            'file',
            'uploaded_at',
            'type'
        ]

        
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
        
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data['email']
        password = data['password']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")

        if user.check_password(password):
            token, created = Token.objects.get_or_create(user=user)
            return {'token': token.key, 'username': user.username}
        else:
            raise serializers.ValidationError("Incorrect password")
        
username_validator = RegexValidator(
    regex=r'^[\w\s]+$',
    message='Enter a valid username. This value may contain letters, numbers, underscores, and spaces.',
    code='invalid_username'
)

class RegistrationSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only= True)
    type = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'repeated_password', 'type']
        extra_kwargs = {
            'password': {'write_only': True},
            'username': {'validators': [username_validator]}
        }
        
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email address is already registered.")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(" This username is already taken.")
        return value
        
    def save(self):
        pw = self.validated_data['password']
        repeated_pw = self.validated_data['repeated_password']
        type = self.validated_data['type']
        
        if pw != repeated_pw:
            raise serializers.ValidationError({'error': 'passwords dont match'})
        
        if User.objects.filter(email=self.validated_data['email']).exists():
            raise serializers.ValidationError({'error': 'Email exists already'})
        
        account = User(email=self.validated_data['email'], username=self.validated_data['username'])
        account.set_password(pw)
        account.save()
        if type == 'business':
            BusinessPartner.objects.create(
                user=account,
                email=account.email,
                type='business'
            )
        else:
            Customer.objects.create(
                user=account,
                type='customer'
            )

        return account