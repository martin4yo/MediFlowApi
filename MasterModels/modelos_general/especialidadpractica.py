from django.db import models
from ..universal import AuditModel, TenantModel

class EspecialidadPractica(AuditModel, TenantModel):
    """ Clase para manejar los datos de paises """
    idespecialidad = models.ForeignKey('Especialidad', on_delete=models.CASCADE)
    idpractica = models.ForeignKey('Practica', on_delete=models.CASCADE)
    preparacion = models.TextField(default='')
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    duracion = models.IntegerField(default=0)
    observaciones = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Practica por Especialidad'
        verbose_name_plural = 'GRAL - Practica por Especialidad'

    def __str__(self):
        return f'{self.idespecialidad.nombre}, {self.idpractica.nombre}'