from django.db import models
from ..universal import AuditModel, TenantModel

class PacienteHistoria(AuditModel, TenantModel):
    """ Clase para manejar los datos de paises """
    idpaciente = models.ForeignKey('Paciente', on_delete=models.CASCADE)
    fecha = models.DateField()
    observaciones = models.TextField()
    
    class Meta:
        verbose_name = 'Historia Clínica'
        verbose_name_plural = 'PACI - Historias por paciente'

    def __str__(self):
        return f'{self.idpaciente.nombre}, {self.fecha}'