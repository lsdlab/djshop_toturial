from django.apps import AppConfig


class TransactionsConfig(AppConfig):
    name = 'apps.transactions'
    verbose_name = "Transactions"

    def ready(self):
        import apps.transactions.signals


default_app_config = 'apps.transactions.TransactionsConfig'
