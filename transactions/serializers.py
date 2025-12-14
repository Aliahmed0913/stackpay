from rest_framework import serializers
from transactions.models import Transaction
from .services.transaction_orchestration import create_transaction

class TransactionSerializer(serializers.ModelSerializer):
    class Meta():
        model = Transaction
        fields = ('customer','amount','status','paymob_order_id','paymob_payment_token','created_at')
        read_only_fields = ('customer','status','paymob_order_id','paymob_payment_token')
        extra_kwargs={
            'amount':{'required':True}
        }
    def validate_amount(self,value):
        if value <= 0:
            raise serializers.ValidationError('Invalid amount')
        return value
    

    