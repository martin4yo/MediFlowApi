from django.db import models
from ..universal import AuditModel, TenantModel

class ProfesionalPractica(AuditModel, TenantModel):
    """ Clase para manejar los datos de paises """
    idprofesional = models.ForeignKey('Profesional', on_delete=models.CASCADE)
    idespecialidadpractica = models.ForeignKey('EspecialidadPractica', on_delete=models.CASCADE)
    duracion = models.IntegerField()
    diasagenda = models.IntegerField()

    class Meta:
        verbose_name = 'Practica por Profesional'
        verbose_name_plural = 'PROS - Practicas por Profesional'

    def __str__(self):
        return f'{self.idprofesional.prefijo}, {self.idprofesional.apellido}, {self.idespecialidadpractica.idespecialidad.nombre}, {self.duracion}, {self.diasagenda}'
    