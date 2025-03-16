from django.db import models
from ..universal import AuditModel, TenantModel

class Centro(AuditModel):
    """ Clase para manejar los roles """
    codigo = models.CharField(max_length=10, default='', unique=True)
    nombre = models.CharField(max_length=200)

    class Meta:
        verbose_name = 'Centro'
        verbose_name_plural = 'GRAL - Centros'

    def __str__(self):
        return f'{self.codigo}, {self.nombre}' 
    
