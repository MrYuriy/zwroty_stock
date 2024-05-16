from django.apps import AppConfig


class ZwrotyConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "zwroty"

    def ready(self):
        from . import signals
