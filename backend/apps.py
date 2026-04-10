from django.apps import AppConfig

class BackendConfig(AppConfig):
    name = 'backend'
    verbose_name = 'Магазин'

    def ready(self):
        import backend.signals