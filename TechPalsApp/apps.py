from django.apps import AppConfig


class TechpalsappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'TechPalsApp'
    
    def ready(self):
        import TechPalsApp.signals


    
