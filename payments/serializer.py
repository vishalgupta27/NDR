from rest_framework import serializers
from accounts.models import BankAccount
from .models import ExtendTransaction
from products.serializers import *

class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = ('id', 'account_holder_name', 'account_number', 'routing_number')

class ExtendTransactionSerializer(serializers.ModelSerializer):
    order_id = serializers.CharField(required = False)
    extendFromDate = serializers.CharField(required = False)
    extendToDate = serializers.CharField(required = False)
    extendAmount = serializers.CharField(required = False)
    class Meta:
        model = ExtendTransaction
        fields = ['order_id','extendFromDate','extendToDate','extendAmount']

class ViewRenterExtendSerializer(serializers.ModelSerializer):
    order = ViewRenterOrderSerializer(read_only = True)
    class Meta:
        model = ExtendTransaction
        fields = '__all__'

class ViewLenderExtendSerializer(serializers.ModelSerializer):
    order = ViewTransactionSerializer(read_only = True)
    class Meta:
        model = ExtendTransaction
        fields = '__all__'