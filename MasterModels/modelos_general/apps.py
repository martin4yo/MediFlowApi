from django.apps import AppConfig


class ModelosGeneralConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'MasterModels.modelos_general'
    label = 'modelos_general'
    verbose_name = 'Modelos Generales'