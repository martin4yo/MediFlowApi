from django.db import models
from ..universal import AuditModel, TenantModel

class Practica(AuditModel, TenantModel):
    """ Clase para manejar los datos de paises """
    codigo = models.CharField(max_length=10, default='', unique=True)
    nombre = models.CharField(max_length=200)
    
    class Meta:
        verbose_name = 'Practica'
        verbose_name_plural = 'GRAL - Practicas'

    def __str__(self):
        return f'{self.codigo}, {self.nombre}'