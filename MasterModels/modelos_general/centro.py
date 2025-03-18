from django.db import models
from ..universal import AuditModel, TenantModel

class Centro(AuditModel):
    """ Clase para manejar los roles """
    codigo = models.CharField(max_length=10, default='', unique=True)
    nombre = models.CharField(max_length=200)
    direccion = models.CharField(max_length=200, blank=True, null=True)
    localidad = models.CharField(max_length=200, blank=True, null=True)
    telefono = models.CharField(max_length=200, blank=True, null=True)
    horario = models.CharField(max_length=200, blank=True, null=True)
    mail = models.EmailField(max_length=200, blank=True, null=True)
    web = models.CharField(max_length=200, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    

    class Meta:
        verbose_name = 'Centro'
        verbose_name_plural = 'GRAL - Centros'

    def __str__(self):
        return f'{self.codigo}, {self.nombre}' 
    
