from django.db.models.signals import pre_save
from django.dispatch import receiver
from rest_framework.exceptions import ValidationError
from .models import Account,Transactions

# to prevent any operation from droping the account balance below zero
@receiver(pre_save, sender=Account)
def validate_current_balance(sender, instance, **kwargs):
    if instance.current_balance < 0:
        raise ValidationError({"error":"Not enough funds."})

# this is to update the balance of the account on every transaction
@receiver(pre_save, sender=Transactions)
def validate_current_balance(sender, instance, **kwargs):
    bank_data = Account.objects.all().first()
    bank_data.current_balance += instance.amount
    bank_data.save()