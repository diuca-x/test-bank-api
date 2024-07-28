from django.db import models

# Create your models here.
class Account(models.Model):
    current_balance = models.FloatField(null=False)



class Transactions(models.Model):
    date = models.DateTimeField(null=False)
    amount = models.FloatField(null=False)
    balance_at_time = models.FloatField(null=False)