from django.db import models
from ..universal import AuditModel, TenantModel

class Paciente(AuditModel, TenantModel):
    """ Clase para manejar los datos de paises """
    nombre = models.CharField(max_length=200)
    apellido = models.CharField(max_length=200)
    documento = models.CharField(max_length=20)
    idgenero = models.ForeignKey('Genero', on_delete=models.CASCADE)
    direccion = models.CharField(max_length=200)
    localidad = models.CharField(max_length=200)
    fechanacimiento = models.DateField()
    ocupacion = models.CharField(max_length=200)
    observaciones = models.TextField()

    class Meta:
        verbose_name = 'Paciente'
        verbose_name_plural = 'PACI - Pacientes'

    def __str__(self):
        return f'{self.apellido}, {self.nombre}, {self.documento}'