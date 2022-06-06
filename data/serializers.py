from rest_framework import serializers
from .models import *


class ItemFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemFile
        fields = '__all__'


class ItemRowSerializer(serializers.ModelSerializer):
    files = ItemFileSerializer(many=True, required=False, read_only=True)
    class Meta:
        model = ItemRow
        fields = '__all__'

class ItemSerializer(serializers.ModelSerializer):
    rows = ItemRowSerializer(many=True,required=False,read_only=True)
    class Meta:
        model = Item
        fields = '__all__'




