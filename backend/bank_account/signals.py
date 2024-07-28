from django.db.models.signals import pre_save
from django.dispatch import receiver
from rest_framework.exceptions import ValidationError
from .models import Account

@receiver(pre_save, sender=Account)
def validate_current_balance(sender, instance, **kwargs):
    if instance.current_balance < 0:
        raise ValidationError({"error":"Not enough funds."})