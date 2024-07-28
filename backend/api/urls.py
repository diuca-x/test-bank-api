from django.urls import path

from . import views
from bank_account import views as bank_view
# here go all the url paths of this api
urlpatterns = [
    path("get-statement/<str:order>",bank_view.StatementListAPIView.as_view()),
    path("deposit",bank_view.MoveMoneyAPIView.as_view()),
    path("withdraw",bank_view.MoveMoneyAPIView.as_view()),
    path("transfer",bank_view.TransferMoneyAPIView.as_view())

]