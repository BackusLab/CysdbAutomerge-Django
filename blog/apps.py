# from django.apps import AppConfig


# class BlogConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'blog'

from django.apps import AppConfig
from django.core.management import call_command
import sys

class BlogConfig(AppConfig):
    name = 'blog'

    def ready(self):
        if 'runserver' in sys.argv:
            try:
                call_command('load_initial_data')
            except Exception as e:
                print(f"Error loading initial data: {e}")

