from django.db import models
from ..universal import AuditModel, TenantModel

class ProfesionalPracticaCentro(AuditModel, TenantModel):
    """ Clase para manejar los datos de paises """
    idprofesionalpracticacentro = models.ForeignKey('ProfesionalPracticaCentro', on_delete=models.CASCADE)
    idcentro = models.ForeignKey('Centro', on_delete=models.CASCADE)
    dias = models.CharField(max_length=7)
    horario = models.TimeField()

    class Meta:
        verbose_name = 'Practica por Profesional/Centro'
        verbose_name_plural = 'PROS - Practicas por Profesional/Centro'

    def __str__(self):
        return f'{self.idprofesionalpracticacentro.idespecialidadpractica.idpractica.nombre}, {self.idprofesional.apellido}, {self.idespecialidadpractica.idespecialidad.nombre}, {self.duracion}, {self.diasagenda}'
    