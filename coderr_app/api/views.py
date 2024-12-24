from rest_framework import generics
from coderr_app.models import Offer, Review
from .serializers import OfferSerializer


class OfferView(generics.ListCreateAPIView):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer

class OfferViewDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    
class ReviewList(generics.ListCreateAPIView):
    queryset = Review.objects.all()
    
class OrdersView(generics.ListCreateAPIView):
    pass 

class OrderCountView(generics.ListCreateAPIView):
    pass 

class CompletedOrderCountView(generics.ListCreateAPIView):
    pass 

class BaseInfoView(generics.ListCreateAPIView):
    pass 

