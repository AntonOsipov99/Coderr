from django.forms import ValidationError
from rest_framework import generics, viewsets, filters
from rest_framework.filters import OrderingFilter
from rest_framework.views import  APIView
from coderr_app.models import Offer, OfferDetail, Order, Review
from .serializers import OfferDetailSerializer, OfferDetailViewSerializer, OfferCreateSerializer, OfferListSerializer, OrderSerializer, CreateOrderSerializer, ReviewSerializer, BaseInfoSerializer, FileUploadSerializer
from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated, AllowAny
from .permissions import IsBusinessUser, IsOwnerOrAdmin, IsCustomer, IsCustomerOrAdminModification
from django.shortcuts import get_object_or_404
from user_auth_app.models import BusinessPartner, Customer
from rest_framework.exceptions import MethodNotAllowed
from .utils import create_order_object, filter_review_query
from rest_framework.decorators import api_view
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Avg
from .paginations import LargeResultsSetPagination
from .utils import OfferFilter

class OfferViewSet(viewsets.ModelViewSet):
    queryset = Offer.objects.all().order_by('id')
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['title', 'description']
    ordering_fields = ['min_price', 'updated_at']
    filterset_class = OfferFilter
    pagination_class = LargeResultsSetPagination
    
    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsBusinessUser]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
        elif self.action == 'retrieve':
            permission_classes = [IsAuthenticated]
        else: 
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update', 'update']:
            return OfferCreateSerializer
        elif self.action == 'retrieve':
            return OfferDetailViewSerializer
        return OfferListSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        creator_id = self.request.query_params.get('creator_id', None)
        if creator_id and creator_id.strip():
            try:
                creator_id = int(creator_id)
                queryset = queryset.filter(user_id=creator_id)
            except ValueError:
                pass
        return queryset

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({}, status=status.HTTP_200_OK)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class OfferDetailViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        offer_id = self.request.query_params.get('offer', None)
        if offer_id is not None:
            queryset = queryset.filter(offer_id=offer_id)
        return queryset
    
class OrdersViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        try:
            business_partner = BusinessPartner.objects.get(user=user)
            return Order.objects.filter(business_user=business_partner)
        except BusinessPartner.DoesNotExist:
            try:
                customer = Customer.objects.get(user=user)
                return Order.objects.filter(customer_user=customer)
            except Customer.DoesNotExist:
                return Order.objects.none()
            
    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        order = create_order_object(
        business=serializer.business,
        customer=serializer.customer,
        offer_detail=serializer.offer_detail
        )
        order_data = OrderSerializer(order).data
        return Response(order_data, status=status.HTTP_201_CREATED)

            
    def update(self, request, *args, **kwargs):
        if request.method != 'PATCH':
            raise MethodNotAllowed('PATCH is the only HTTP method allowed for this endpoint.')
        return super().update(request, *args, **kwargs)
    
    
    def destroy(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise ValidationError('You do not have permission to delete orders.')
        super().destroy(request, *args, **kwargs)
        return Response({}, status=status.HTTP_200_OK) 

@api_view(['GET'])
def get_order_count(request, business_user_id):
    try:
        business_user = BusinessPartner.objects.get(id=business_user_id)
        order_count = Order.objects.filter(
            business_user=business_user,
            status='in_progress'
        ).count()
        return Response({'order_count': order_count})
    except ObjectDoesNotExist:
        return Response(
            {'error': 'Business user not found.'}, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['GET'])
def get_completed_order_count(request, business_user_id):
    try:
        business_user = BusinessPartner.objects.get(id=business_user_id)
        completed_count = Order.objects.filter(
            business_user=business_user,
            status='completed'
        ).count()
        return Response({'completed_order_count': completed_count})
    except ObjectDoesNotExist:
        return Response(
            {'error': 'Business user not found.'}, 
            status=status.HTTP_404_NOT_FOUND
        )

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsCustomerOrAdminModification]
    filter_backends = [OrderingFilter]
    ordering_fields = ['updated_at', 'rating']
    
    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            permission_classes = [IsCustomerOrAdminModification]
        else:
            permission_classes = [IsCustomer]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        try:
            queryset = Review.objects.all()
            queryset = filter_review_query(self, queryset)
            return queryset
        except Exception as e:
            raise ValidationError({
                'error': 'Error fetching reviews',
                'detail': str(e)
            })
            
    def get_customer_or_raise_error(self):
        try:
            return Customer.objects.get(user=self.request.user)
        except Customer.DoesNotExist:
            raise ValidationError({
            'error': 'Customer profile not found',
            'detail': 'You must have a customer profile to create reviews'
            })
        
    def perform_create(self, serializer):
        customer = self.get_customer_or_raise_error()
        existing_review = Review.objects.filter(
            business_user=serializer.validated_data['business_user'],
            reviewer=customer
        ).exists()
        if existing_review:
            raise ValidationError({
            'error': 'Duplicate review',
            'detail': 'You have already reviewed this business user'
            })
        serializer.save(reviewer=customer)

class BaseInfoView(generics.GenericAPIView):
    serializer_class = BaseInfoSerializer
    
    def get(self, request, format=None):
        review_count = Review.objects.count()
        average_rating = Review.objects.aggregate(Avg('rating'))['rating__avg'] or 0
        business_profile_count = BusinessPartner.objects.count()
        offer_count = Offer.objects.count()
        data = {
            'review_count': review_count,
            'average_rating': round(average_rating, 1),
            'business_profile_count': business_profile_count,
            'offer_count': offer_count,
        }
        serializer = self.get_serializer(data=data)
        serializer.is_valid()        
        return Response(serializer.data)

class FileUploadView(APIView):
    def post(self, request, format=None):
        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)