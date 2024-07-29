from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from django.utils import timezone
from .models import Transactions,Account,operation_type

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
            "operation"
        ]
    def get_date(self,obj):
        return obj.date.date()

# serialzier for the statement list validation of the incoming data
class StatementRequestSerializer(serializers.Serializer):
    operation_type = serializers.ChoiceField(choices=[(tag.value,tag.name) for tag in operation_type],required=False,allow_null=True)
    dates = serializers.ListField(child=serializers.DateField(input_formats=['%d-%m-%Y'],format='%d-%m-%Y'),min_length=2,max_length=2,required=False,allow_null=True)
    order = serializers.ChoiceField(choices=["asc","desc"],required=False,allow_null=True)

# to make the pagination
class CustomPagination(PageNumberPagination):
    page_size = 10  

    def paginate_queryset(self, queryset, request, view=None):
        page = request.query_params.get("page")
        if page == "first":
            request.query_params._mutable = True
            request.query_params['page'] = 1
            request.query_params._mutable = True
        elif page == "last":
            paginator = self.django_paginator_class(queryset, self.page_size)
            request.query_params._mutable = True
            request.query_params['page'] = paginator.num_pages
            request.query_params._mutable = True
        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        return Response({
            "page": self.page.number,
            "total_pages":self.page.paginator.num_pages,
            "links": {
                "next": self.get_next_link(),
                "previous": self.get_previous_link()
            },
            "data": data
        })
    
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
        validated_data["operation"] = self.context.get("operation")

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
