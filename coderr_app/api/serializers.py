from rest_framework import serializers
from coderr_app.models import FileUpload
from coderr_app.models import Offer, OfferDetail
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username']
        
class OfferDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferDetail
        fields = '__all__' 

class OfferSerializer(serializers.ModelSerializer):
    details = OfferDetailSerializer(many=True, read_only=True)
    user_details = UserSerializer(read_only=True) 

    class Meta:
        model = Offer
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
        
class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileUpload
        fields = ['file', 'uploaded_at']