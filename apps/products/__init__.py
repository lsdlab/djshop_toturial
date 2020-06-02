from django.apps import AppConfig


class ProductsConfig(AppConfig):
    name = 'apps.products'
    verbose_name = "Products"

    def ready(self):
        import apps.products.signals


default_app_config = 'apps.products.ProductsConfig'
