from rest_framework import serializers
from .models import *


class ItemFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemFile
        fields = '__all__'




class MonthSerializer(serializers.ModelSerializer):
    class Meta:
        model = Month
        fields = '__all__'




class ItemRowSerializer(serializers.ModelSerializer):
    files = ItemFileSerializer(many=True, required=False, read_only=True)
    month = MonthSerializer(many=False, required=False, read_only=True)
    class Meta:
        model = ItemRow
        fields = '__all__'

class RowMonthAmountSerializer(serializers.ModelSerializer):
    # month = MonthSerializer(many=False, required=False, read_only=True)
    class Meta:
        model = RowMonthAmount
        fields = '__all__'

class ItemAccountSerializer(serializers.ModelSerializer):
    rows = ItemRowSerializer(many=True, required=False, read_only=True)
    month_amount = RowMonthAmountSerializer(many=True, required=False, read_only=True)
    class Meta:
        model = ItemAccount
        fields = '__all__'

class ItemSerializer(serializers.ModelSerializer):
    accounts = ItemAccountSerializer(many=True,required=False,read_only=True)
    class Meta:
        model = Item
        fields = '__all__'




