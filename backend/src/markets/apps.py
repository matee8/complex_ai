from django.apps import AppConfig

from markets import prediction


class MarketsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'markets'

    def ready(self):
        prediction.load_all_models()
