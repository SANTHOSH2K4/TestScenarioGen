from django.contrib import admin
from django.apps import apps
from .models import *  

app_models = apps.get_app_config('chat').get_models()

# Register all models in the app dynamically
for model in app_models:
    admin.site.register(model)
