from rest_framework import generics, viewsets
from rest_framework.views import  APIView
from coderr_app.models import Offer, OfferDetail, Review
from .serializers import OfferSerializer, FileUploadSerializer
from rest_framework.response import Response
from rest_framework import status


class OfferViewSet(viewsets.ModelViewSet):
    serializer_class = OfferSerializer
    # permission_classes = [IsAuthenticated]
    queryset = Offer.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

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

class FileUploadView(APIView):
    def post(self, request, format=None):
        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)