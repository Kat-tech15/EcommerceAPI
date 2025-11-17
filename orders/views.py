from rest_framework import permissions,generics, status
from rest_framework.response import Response
from .serializers import OrderSerializer
from .models import Order


class OrderListView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def delete(self, request, *args, **kwargs):
        self.destroy(request, *args, **kwargs)
        return Response({'message': 'Order cancelled succesfully.'}, status=status.HTTP_200_OK)