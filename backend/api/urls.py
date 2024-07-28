from django.urls import path

from . import views
from bank_account import views as bank_view

urlpatterns = [
    path("get-statement",bank_view.StatementListAPIView.as_view()),
    path("deposit",bank_view.DepositMoneyAPIView.as_view()),
    path("withdraw",bank_view.WithdrawMoneyAPIView.as_view()),
    #path("transfer",bank_view.WithdrawMoneyAPIView.as_view())

]