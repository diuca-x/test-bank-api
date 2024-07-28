from rest_framework import generics,status,mixins
from django.db import transaction
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError,NotFound

from .models import Transactions,Account
from .serializers import TransactionsSerializer,MoneyMovementSerializer,TransferSerializer

import datetime

# route to retrieve the bank statement, by asc or desc order
class StatementListAPIView(mixins.ListModelMixin,generics.GenericAPIView):
    serializer_class = TransactionsSerializer

    def get_queryset(self):
        query = Transactions.objects.all()
        order = self.kwargs.get("order")
        if(order == "asc"):
            query = query.order_by("date")
        elif(order == "desc"):
            query = query.order_by("-date")
        else:
            raise NotFound(detail={"message":"invalid url"})
        return query

    def get(self, request, *args, **kwargs):
            queryset = self.get_queryset()
            if not queryset.exists():
                return Response({'message': 'No transactions found.'}, status=status.HTTP_204_NO_CONTENT)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
    
    

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
    
    @transaction.atomic
    def perform_create(self, serializer):
        
        transaction = {
            "amount" : serializer.validated_data.get("amount"),
            "operation": "transfer"
        }
        to_add = MoneyMovementSerializer(data=transaction, context={"operation":"transfer"})
        if(to_add.is_valid()):
            to_add.save()
        else:
            raise ValidationError(code=400, detail="An error has occured")
        
        
