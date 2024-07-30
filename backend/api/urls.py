from django.urls import path

from bank_account import views as bank_view
# here go all the url paths of this api
urlpatterns = [
    path("get-statement",bank_view.StatementListAPIView.as_view(),name="get-statement"),
    path("deposit",bank_view.MoveMoneyAPIView.as_view(),name="deposit"),
    path("withdraw",bank_view.MoveMoneyAPIView.as_view()),
    path("transfer",bank_view.TransferMoneyAPIView.as_view()),
]