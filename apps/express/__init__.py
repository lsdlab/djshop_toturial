from django.apps import AppConfig


class ExpressConfig(AppConfig):
    name = 'apps.express'
    verbose_name = "Express"

    def ready(self):
        import apps.express.signals


default_app_config = 'apps.express.ExpressConfig'
