from rest_framework import serializers

from django.utils import timezone
from .models import Transactions,Account

from schwifty import IBAN

# basic serializer for the Transaction model, only used to fetch data
class TransactionsSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model=Transactions
        fields = [
            "date",
            "amount",
            "balance_at_time",
        ]
    def get_date(self,obj):
        return obj.date.date()

# serializer for the Transaction model in case of withdraw or deposit, it takes the amount to be taken or deposited and creates the rest
# of the fields to save a Transactions instance
class MoneyMovementSerializer(serializers.ModelSerializer):
    class Meta:
        model=Transactions
        fields = [
            "amount",
        ]

    def validate(self, data):
        if hasattr(self, 'initial_data'):
            unknown_keys = set(self.initial_data.keys()) - set(self.fields.keys())
            if unknown_keys:
                raise serializers.ValidationError({"Got unexpected fields: ": list(unknown_keys)})
        return data
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

    def create(self, validated_data):
        validated_data['date'] = timezone.now()
        if (self.context.get("operation") == "deposit"):
            validated_data['balance_at_time'] = Account.objects.all().first().current_balance + validated_data.get("amount")
        elif (self.context.get("operation") == "withdraw" or self.context.get("operation") == "transfer"):
            validated_data['balance_at_time'] = Account.objects.all().first().current_balance - validated_data.get("amount")
            validated_data["amount"] = -validated_data["amount"]
        else: 
            raise serializers.ValidationError("Error in operation")
        return super().create(validated_data)

# serializer for the transference of data, it validates the amount and the IBAN account number
class TransferSerializer(serializers.Serializer):
    amount = serializers.FloatField()
    account = serializers.CharField(max_length=34)

    def validate(self, data):
        if hasattr(self, 'initial_data'):
            unknown_keys = set(self.initial_data.keys()) - set(self.fields.keys())
            if unknown_keys:
                raise serializers.ValidationError({"Got unexpected fields: ": list(unknown_keys)})
        return data
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value
    
    def validate_account(self,value):

        try:
            IBAN(value)
        except Exception as error:
            raise serializers.ValidationError((error))

        return value
