from django.db import models
from ..universal import AuditModel, TenantModel

class Cobertura(AuditModel, TenantModel):
    """ Clase para manejar los datos de paises """
    codigo = models.CharField(max_length=10, default='', unique=True)
    nombre = models.CharField(max_length=200)
    
    class Meta:
        verbose_name = 'Cobertura'
        verbose_name_plural = 'GRAL - Coberturas'

    def __str__(self):
        return f'{self.codigo}, {self.nombre}'