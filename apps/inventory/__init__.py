from django.apps import AppConfig


class InventoryConfig(AppConfig):
    name = 'apps.inventory'
    verbose_name = "Inventory"

    def ready(self):
        import apps.inventory.signals


default_app_config = 'apps.inventory.InventoryConfig'
