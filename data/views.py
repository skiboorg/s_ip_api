from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import *


class GetItems(generics.ListAPIView):
    serializer_class = ItemSerializer
    queryset = Item.objects.all()

class GetItem(generics.RetrieveAPIView):
    serializer_class = ItemSerializer

    def get_object(self):
        return Item.objects.get(id=self.request.query_params.get('id'))