from django.apps import AppConfig


class ArandnwConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'arandnw'

    def ready(self):
        import arandnw.signals