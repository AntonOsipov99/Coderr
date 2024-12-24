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
        fields = ['id', 'title', 'revisions', 'delivery_time_in_days', 'price', 
                 'features', 'type']

    def validate_revisions(self, value):
        if value < -1:
            raise serializers.ValidationError("Revisions must be -1 (unlimited) or a positive number.")
        return value

    def validate_delivery_time_in_days(self, value):
        if value < 1:
            raise serializers.ValidationError("Delivery time must be a positive number.")
        return value

    def validate_features(self, value):
        if not value or len(value) == 0:
            raise serializers.ValidationError("At least one feature must be specified.")
        return value

class OfferSerializer(serializers.ModelSerializer):
    details = OfferDetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = [
            'id',
            'user',
            'title',
            'image',
            'description',
            'created_at',
            'updated_at',
            'details'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def create(self, validated_data):
        details_data = validated_data.pop('details')
        
        # Validiere Anzahl der Details
        if len(details_data) != 3:
            raise serializers.ValidationError("Exactly three offer details are required.")
        
        # Validiere Typen der Details
        types = set(detail['offer_type'] for detail in details_data)
        required_types = {'basic', 'standard', 'premium'}
        if types != required_types:
            raise serializers.ValidationError(
                "Exactly one detail of each type (basic, standard, premium) is required."
            )
        
        # Erstelle das Offer
        offer = Offer.objects.create(**validated_data)
        
        # Erstelle die Details
        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)
        
        return offer
    
class OfferDetailCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferDetail
        fields = ['title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type']
        
class OfferDetailListSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ['id', 'url']

    def get_url(self, obj):
        return f"/offerdetails/{obj.id}/"
        
class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileUpload
        fields = ['file', 'uploaded_at']