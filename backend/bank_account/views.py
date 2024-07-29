from rest_framework import generics,status,mixins
from django.db import transaction
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError,NotFound

from .models import Transactions,Account
from .serializers import TransactionsSerializer,MoneyMovementSerializer,TransferSerializer,StatementRequestSerializer,CustomPagination
from .scripts import filter_query
import datetime

# route to retrieve the bank statement, by asc or desc order
class StatementListAPIView(mixins.ListModelMixin,generics.GenericAPIView):
    request_serializer_class = StatementRequestSerializer
    response_serializer_class = TransactionsSerializer

    pagination_class=CustomPagination

    queryset = Transactions.objects.all()

    

    def post(self, request, *args, **kwargs):
        request_serializer = self.request_serializer_class(data=request.data)    

        if(request_serializer.is_valid()):
            filters = request_serializer.validated_data
            queryset = self.get_queryset()   

            filtered_query = filter_query(queryset,filters)
            if not filtered_query.exists():
                return Response({'message': 'No transactions found.'}, status=status.HTTP_204_NO_CONTENT)

            page = self.paginate_queryset(filtered_query)
            if page is not None:
                response_serializer = self.response_serializer_class(page, many=True)
                return self.get_paginated_response(response_serializer.data)
        else:
            raise ValidationError(code=400,detail=request_serializer.errors)         
        
        
        
    
    

# route to deposit or withdraw money
class MoveMoneyAPIView(generics.CreateAPIView):
    queryset = Transactions.objects.all()
    serializer_class = MoneyMovementSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        operation = self.request.path.strip('/').split('/')[-1]
        if(operation == "deposit"):
            context["operation"] = "deposit"
        elif(operation == "withdraw"):
            context["operation"] = "withdraw"
        else:
            raise ValidationError(code=404,detail="An unexpected error has occured")
        return context

    @transaction.atomic
    def perform_create(self, serializer):
        # on saves it calls the create method from the serializer
        serializer.save()
        
        

# route to transfer money to another account using the IBAN number
class TransferMoneyAPIView(generics.CreateAPIView):
    queryset = Transactions.objects.all()
    serializer_class = TransferSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        operation = self.request.path.strip('/').split('/')[-1]
        if(operation == "transfer"):
            context["operation"] = "transfer"
        else:
            raise ValidationError(code=404,detail="An unexpected error has occured")
        return context
    
    @transaction.atomic
    def perform_create(self, serializer):
        
        transaction = {
            "amount" : serializer.validated_data.get("amount"),
        }
        to_add = MoneyMovementSerializer(data=transaction, context={"operation":"transfer"})
        if(to_add.is_valid()):
            to_add.save()
        else:
            print(to_add.errors)
            raise ValidationError(code=400, detail="An error has occured")
        
        
