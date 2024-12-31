from rest_framework import serializers
from coderr_app.models import Offer, OfferDetail, Order, Review, FileUpload, BaseInfo
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from user_auth_app.models import Customer
from .utils import order_references_and_validate

class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'username']
        
class OfferDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferDetail
        fields = ['id', 'title', 'revisions', 'delivery_time_in_days', 'price',
                 'features', 'offer_type']
    
class OfferDetailViewSerializer(serializers.ModelSerializer):
    details = OfferDetailSerializer(many=True, read_only=True)
    user_details = UserDetailSerializer(source='user', read_only=True)

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
            'details',
            'min_price',
            'min_delivery_time',
            'user_details'
        ]
    
class OfferDetailURLSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ['id', 'url']

    def get_url(self, obj):
        return f"/offerdetails/{obj.id}/"

class OfferCreateSerializer(serializers.ModelSerializer):
    details = OfferDetailSerializer(many=True)
    user_details = UserDetailSerializer(source='user', read_only=True)
    class Meta:
        model = Offer
        fields = [
            'id',
            'title',
            'image',
            'description',
            'details',
            'user_details'
        ]
    
    def create(self, validated_data):
        details_data = validated_data.pop('details')
        basic_detail = next(d for d in details_data if d['offer_type'] == 'basic')
        validated_data['min_price'] = basic_detail['price']
        validated_data['min_delivery_time'] = basic_detail['delivery_time_in_days']
        validated_data['user'] = self.context['request'].user
        offer = Offer.objects.create(**validated_data)
        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)
        return offer

    def update(self, instance, validated_data):
        details_data = validated_data.pop('details', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)       
        if details_data is not None:
            instance.details.all().delete()
            for detail_data in details_data:
                OfferDetail.objects.create(offer=instance, **detail_data)
            basic_detail = next(d for d in details_data if d['offer_type'] == 'basic')
            instance.min_price = basic_detail['price']
            instance.min_delivery_time = basic_detail['delivery_time_in_days']
        instance.save()
        return instance
    
class OfferListSerializer(serializers.ModelSerializer):
    details = OfferDetailURLSerializer(many=True, read_only=True)
    user_details = UserDetailSerializer(source='user', read_only=True)

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
            'details',
            'min_price',
            'min_delivery_time',
            'user_details'
        ]

class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = '__all__'
        
class CreateOrderSerializer(serializers.Serializer):
    offer_detail_id = serializers.IntegerField()

    def validate(self, data):
        authenticated_user = self.context['request'].user
        offer_detail_id = data.get('offer_detail_id')
        offer_detail, customer, business = order_references_and_validate(offer_detail_id, authenticated_user)
        self.offer_detail, self.customer, self.business = offer_detail, customer, business
        return data
    
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'business_user', 'reviewer', 'rating', 
                 'description', 'created_at', 'updated_at']
        read_only_fields = ['reviewer', 'created_at', 'updated_at']
        
class BaseInfoSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = BaseInfo
        fields = '__all__'

        
class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileUpload
        fields = ['file', 'uploaded_at']