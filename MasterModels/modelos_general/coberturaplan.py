from django.db import models
from ..universal import AuditModel, TenantModel

class CoberturaPlan(AuditModel, TenantModel):
    """ Clase para manejar los datos de paises """
    codigo = models.CharField(max_length=10, default='', unique=True)
    nombre = models.CharField(max_length=200)
    idcobertura = models.ForeignKey('Cobertura', on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = 'Plan por Cobertura'
        verbose_name_plural = 'GRAL - Planes por Cobertura'

    def __str__(self):
        return f'{self.idcobertura.nombre}, {self.nombre}'