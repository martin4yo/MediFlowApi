from django.db import models
from ..universal import AuditModel, TenantModel

class Profesional(AuditModel, TenantModel):
    """ Clase para manejar los datos de paises """
    nombre = models.CharField(max_length=200)
    apellido = models.CharField(max_length=200)
    prefijo = models.CharField(max_length=10)
    idgenero = models.ForeignKey('Genero', on_delete=models.CASCADE)
    direccion = models.CharField(max_length=200)
    localidad = models.CharField(max_length=200)
    fechanacimiento = models.DateField()
    observaciones = models.TextField()

    class Meta:
        verbose_name = 'Profesional'
        verbose_name_plural = 'PROS - Profesionales'

    def __str__(self):
        return f'{self.prefijo}, {self.apellido}, {self.nombre}'