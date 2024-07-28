from rest_framework import generics,status
from django.db import transaction
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from .models import Transactions,Account
from .serializers import TransactionsSerializer,MoneyMovementSerializer,TransferSerializer

import datetime

# route to retrieve the bank statement, ordered by most recent by default
class StatementListAPIView(generics.ListAPIView):
    queryset = Transactions.objects.all().order_by('-date')
    serializer_class = TransactionsSerializer

    def list(self, request, *args, **kwargs):
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
        operation = self.get_serializer_context().get("operation")
        serializer.save()
        
        

# route to transfer money to another account using the IBAN number
class TransferMoneyAPIView(generics.CreateAPIView):
    queryset = Transactions.objects.all()
    serializer_class = TransferSerializer
    
    @transaction.atomic
    def perform_create(self, serializer):
        
        transaction = {
            "amount" : serializer.validated_data.get("amount")
        }
        to_add = MoneyMovementSerializer(data=transaction, context={"operation":"transfer"})
        if(to_add.is_valid()):
            to_add.save()
        else:
            raise ValidationError(code=400, detail="An error has occured")
        
        
