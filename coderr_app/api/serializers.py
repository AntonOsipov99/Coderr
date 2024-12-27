from rest_framework import serializers
from coderr_app.models import Offer, OfferDetail, Order, FileUpload
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated

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
            'title',
            'image',
            'description',
            'details',
            'user_details'
        ]

    def validate_details(self, details):
        if len(details) != 3:
            raise ValidationError("Genau drei Angebotsdetails (basic, standard, premium) sind erforderlich.")
        
        required_types = {'basic', 'standard', 'premium'}
        provided_types = {detail['offer_type'] for detail in details}
        
        if provided_types != required_types:
            raise ValidationError(
                f"Die Angebotstypen müssen genau basic, standard und premium sein."
            )
        
        # Validate price order (basic < standard < premium)
        prices = {detail['offer_type']: detail['price'] for detail in details}
        if not (prices['basic'] < prices['standard'] < prices['premium']):
            raise ValidationError("Die Preise müssen aufsteigend sein: basic < standard < premium")
        
        return details

    def create(self, validated_data):
        details_data = validated_data.pop('details')
        
        # Set min_price and min_delivery_time from basic package
        basic_detail = next(d for d in details_data if d['offer_type'] == 'basic')
        validated_data['min_price'] = basic_detail['price']
        validated_data['min_delivery_time'] = basic_detail['delivery_time_in_days']
        validated_data['user'] = self.context['request'].user
        offer = Offer.objects.create(**validated_data)
        
        # Create the details
        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)
        
        return offer

    def update(self, instance, validated_data):
        details_data = validated_data.pop('details', None)
        
        # Update the offer instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if details_data is not None:
            # Delete existing details
            instance.details.all().delete()
            
            # Create new details
            for detail_data in details_data:
                OfferDetail.objects.create(offer=instance, **detail_data)
            
            # Update min_price and min_delivery_time
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

    def validate_offer_detail_id(self, value):
        try:
            Order.objects.get(id=value)
            return value
        except Order.DoesNotExist:
            raise serializers.ValidationError("Angebot mit dieser ID existiert nicht.")

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
        
class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileUpload
        fields = ['file', 'uploaded_at']