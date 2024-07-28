from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from django.utils import timezone
from .models import Transactions,Account


class TransactionsSerializer(serializers.ModelSerializer):
    class Meta:
        model=Transactions
        fields = [
            "date",
            "amount",
            "balance_at_time",
        ]

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
                raise ValidationError({"Got unexpected fields: ": list(unknown_keys)})
        return data
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

    def create(self, validated_data):
        validated_data['date'] = timezone.now()
        if (self.context.get("operation") == "deposit"):
            validated_data['balance_at_time'] = Account.objects.all().first().current_balance + validated_data.get("amount")
        elif (self.context.get("operation") == "withdraw"):
            validated_data['balance_at_time'] = Account.objects.all().first().current_balance - validated_data.get("amount")
            validated_data["amount"] = -validated_data["amount"]
        else: 
            raise serializers.ValidationError("Error in operation")
        return super().create(validated_data)
    
class TransferSerializer(serializers.Serializer):
    amount = serializers.FloatField()
    account = serializers.CharField(max_length=34)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value
