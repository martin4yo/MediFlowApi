# """ admin """
# from django.contrib import admin
# from django.apps import apps

# from MasterModels.modelos_general import * 
# from MasterModels.modelos_contabilidad import *
# from MasterModels.modelos_entidad import *
# from MasterModels.modelos_impuestos import *
# from MasterModels.modelos_producto import *

# # Lista de tus aplicaciones, definidas en INSTALLED_APPS
# my_apps =   [
#             'MasterModels', 
#             ]  # Reemplaza con los nombres de tus aplicaciones

# # Itera sobre las aplicaciones que has creado
# for app_label in my_apps:
#     app_config = apps.get_app_config(app_label)
#     models = app_config.get_models()

#     # Itera sobre los modelos de la aplicación y regístralos en el admin
#     for model in models:
#         try:
            
#             admin.site.register(model)
#         except admin.sites.AlreadyRegistered:
#             # Ya está registrado, omitir
#             pass

# Modelo CON INLINES AUTOMATICOS

""" admin """
from django.contrib import admin
from django.apps import apps
from django.db.models import ForeignKey

from MasterModels.modelos_general import * 
from MasterModels.modelos_profesionales import * 
from MasterModels.modelos_pacientes import * 

# Lista de tus aplicaciones, definidas en INSTALLED_APPS
my_apps = [
    'MasterModels',
]  # Reemplaza con los nombres de tus aplicaciones

# Función para crear un Inline automáticamente
def create_inline(model, fk_name=None):
    attrs = {
        "model": model,
        "extra": 1,
    }
    if fk_name:
        attrs["fk_name"] = fk_name  # Definir fk_name dinámicamente

    return type(f"{model.__name__}Inline", (admin.TabularInline,), attrs)

# Diccionario para almacenar inlines por modelo maestro
admin_registry = {}

# Iterar sobre las aplicaciones y registrar modelos
for app_label in my_apps:
    app_config = apps.get_app_config(app_label)
    models = app_config.get_models()

    for model in models:
        try:
            # Verificar si el modelo tiene ForeignKeys apuntando a otro modelo
            foreign_keys = [
                field for field in model._meta.get_fields()
                if isinstance(field, ForeignKey)
            ]
            if foreign_keys:
                # Registrar el modelo como inline en el admin del modelo relacionado
                for fk in foreign_keys:
                    related_model = fk.related_model

                    # Crear dinámicamente el Inline con fk_name si es necesario
                    inline = create_inline(model, fk_name=fk.name if len(foreign_keys) > 1 else None)

                    # Agregar el Inline al modelo relacionado
                    if related_model not in admin_registry:
                        admin_registry[related_model] = []
                    
                    admin_registry[related_model].append(inline)

                       # 🔹 **Registrar también el modelo de forma independiente**
                    if model not in admin.site._registry:
                        admin.site.register(model)

            else:
                # Registrar modelos sin ForeignKeys
                admin.site.register(model)
        except admin.sites.AlreadyRegistered:
            # Ya está registrado, omitir
            pass

# Registrar modelos maestros con sus inlines
for master_model, inlines in admin_registry.items():
    admin_class = type(
        f"{master_model.__name__}Admin",
        (admin.ModelAdmin,),
        {"inlines": inlines}
    )
    try:
        admin.site.unregister(master_model)
    except admin.sites.NotRegistered:
        pass
    admin.site.register(master_model, admin_class)
