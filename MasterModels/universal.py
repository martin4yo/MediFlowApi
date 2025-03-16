# Clase general de auditoria #######################################################

from django.db import models

"""
Modelo de datos para campos de auditoria
"""
class AuditModel(models.Model):
    """ Clase abstracta de auditoria para todas las clases """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    disabled = models.BooleanField(default=False)
    user_id = models.ForeignKey('Persona', on_delete=models.CASCADE, blank=True, null=True)
    

    class Meta:
        """ Seteo de clase abstracta """
        abstract = True

class TenantModel(models.Model):
    tenant_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        abstract = True

from django.apps import apps

def listar_tablas_modelos():
    modelos = apps.get_models()
    return [model._meta.db_table for model in modelos]