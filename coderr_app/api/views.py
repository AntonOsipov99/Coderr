from rest_framework import generics, viewsets, filters
from rest_framework.views import  APIView
from coderr_app.models import Offer, OfferDetail, Order, Review
from .serializers import OfferDetailSerializer, OfferDetailViewSerializer, FileUploadSerializer, OfferCreateSerializer, OfferListSerializer, OrderSerializer, CreateOrderSerializer
from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated, AllowAny
from .permissions import IsBusinessUser, IsOwnerOrAdmin
from django.shortcuts import get_object_or_404



class OfferViewSet(viewsets.ModelViewSet):
    queryset = Offer.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['title', 'description']
    ordering_fields = ['min_price', 'created_at']
    filterset_fields = {
        'user': ['exact'],
        'min_price': ['gte', 'lte'],
    }
    
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
        if creator_id is not None:
            queryset = queryset.filter(user_id=creator_id)
        return queryset

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({}, status=status.HTTP_200_OK)
    
    def create(self, request, *args, **kwargs):
        # Add the authenticated user to the request data
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
    
class OrdersView(generics.ListCreateAPIView):
    pass
#     serializer_class = OrderSerializer
#     # permission_classes = [IsAuthenticated]
    
#     def get_queryset(self):
#         user = self.request.user
#         user_profile = UserProfile.objects.get(user=user)
        
#         if user_profile.type == 'business':
#             return Order.objects.filter(business_user=user)
#         else:  # customer
#             return Order.objects.filter(customer_user=user)
    
#     def get_serializer_class(self):
#         if self.request.method == 'POST':
#             return CreateOrderSerializer
#         return OrderSerializer
    
#     def create(self, request, *args, **kwargs):
#         # Überprüfen, ob der User ein Customer ist
#         try:
#             user_profile = UserProfile.objects.get(user=request.user)
#             if user_profile.type != 'customer':
#                 return Response(
#                     {"error": "Nur Kunden können Bestellungen erstellen."},
#                     status=status.HTTP_403_FORBIDDEN
#                 )
#         except UserProfile.DoesNotExist:
#             return Response(
#                 {"error": "Benutzerprofil nicht gefunden."},
#                 status=status.HTTP_404_NOT_FOUND
#             )

#         # Validiere die Eingabedaten
#         create_serializer = CreateOrderSerializer(data=request.data)
#         if not create_serializer.is_valid():
#             return Response(
#                 create_serializer.errors,
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         try:
#             # Offer Detail abrufen
#             offer_detail = Order.objects.get(
#                 id=create_serializer.validated_data['offer_detail_id']
#             )

#             # Neue Bestellung erstellen
#             order = Order.objects.create(
#                 customer_user=request.user,
#                 business_user=offer_detail.business_user,
#                 title=offer_detail.title,
#                 revisions=offer_detail.revisions,
#                 delivery_time_in_days=offer_detail.delivery_time_in_days,
#                 price=offer_detail.price,
#                 features=offer_detail.features,
#                 offer_type=offer_detail.offer_type,
#                 status='in_progress'
#             )

#             # Serialisierte Antwort zurückgeben
#             response_serializer = OrderSerializer(order)
#             return Response(
#                 response_serializer.data,
#                 status=status.HTTP_201_CREATED
#             )

#         except Order.DoesNotExist:
#             return Response(
#                 {"error": "Angebot nicht gefunden"},
#                 status=status.HTTP_404_NOT_FOUND
#             )
#         except Exception as e:
#             return Response(
#                 {"error": str(e)},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
    
class OrdersDetailView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
class ReviewList(generics.ListCreateAPIView):
    queryset = Review.objects.all()

class OrderCountView(generics.ListCreateAPIView):
    pass 

class CompletedOrderCountView(generics.ListCreateAPIView):
    pass 

class BaseInfoView(generics.ListCreateAPIView):
    pass 

class FileUploadView(APIView):
    def post(self, request, format=None):
        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)