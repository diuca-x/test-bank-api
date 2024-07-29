from django.db import models

from enum import Enum


class operation_type(Enum):
    TRANSFER = "transference"
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"


# account model to register the current balance
class Account(models.Model):
    current_balance = models.FloatField(null=False)


# this model is to keep track of the date,amount and the balance at the time of the transaction (deposit,withdraw or transference)
class Transactions(models.Model):
    date = models.DateTimeField(null=False)
    amount = models.FloatField(null=False)
    balance_at_time = models.FloatField(null=False)
    operation = models.CharField(max_length=10)

