from django.apps import AppConfig


class BankAccountConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bank_account'

    def ready(self):
        import bank_account.signals
        return super().ready()
