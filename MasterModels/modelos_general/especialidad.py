from django.db import models
from ..universal import AuditModel, TenantModel

class Especialidad(AuditModel):
    """ Clase para manejar los roles """
    codigo = models.CharField(max_length=10, default='', unique=True)
    nombre = models.CharField(max_length=200)

    class Meta:
        verbose_name = 'Especialidad'
        verbose_name_plural = 'GRAL - Especialidad'

    def __str__(self):
        return f'{self.codigo}, {self.nombre}' 
    
