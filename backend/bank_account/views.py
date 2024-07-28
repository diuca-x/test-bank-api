from rest_framework import generics
from django.db import transaction
from rest_framework.response import Response
from rest_framework import status
from .models import Transactions,Account
from .serializers import TransactionsSerializer,DepositSerializer

import datetime

# stays
class StatementListAPIView(generics.ListAPIView):
    queryset = Transactions.objects.all().order_by('-date')
    serializer_class = TransactionsSerializer
    # lookup_field = "pk"

    def list(self, request, *args, **kwargs):
            queryset = self.get_queryset()
            if not queryset.exists():
                return Response({'message': 'No transactions found.'}, status=status.HTTP_204_NO_CONTENT)
            
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

# stays
class DepositMoneyAPIView(generics.CreateAPIView):
    queryset = Transactions.objects.all().order_by('-date')
    serializer_class = DepositSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["operation"] = "deposit"
        return context

    @transaction.atomic
    def perform_create(self, serializer):
        serializer.save()
        
        bank_data = Account.objects.all().first()
        bank_data.current_balance += serializer.validated_data.get("amount")
        bank_data.save()

# stays
class WithdrawMoneyAPIView(generics.CreateAPIView):
    queryset = Transactions.objects.all().order_by('-date')
    serializer_class = DepositSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["operation"] = "withdraw"
        return context
    
    @transaction.atomic
    def perform_create(self, serializer):
        serializer.save()
        
        bank_data = Account.objects.all().first()
        bank_data.current_balance -= serializer.validated_data.get("amount")
        bank_data.save()