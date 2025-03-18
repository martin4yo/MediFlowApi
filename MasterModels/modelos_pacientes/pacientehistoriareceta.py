from django.db import models
from ..universal import AuditModel, TenantModel

class PacienteHistoriaReceta(AuditModel, TenantModel):
    """ Clase para manejar los datos de paises """
    idpacientehistoria = models.ForeignKey('PacienteHistoria', on_delete=models.CASCADE)
    prescripcion = models.TextField()
    indicaciones = models.TextField()
    observaciones = models.TextField()

    class Meta:
        verbose_name = 'Historia Receta'
        verbose_name_plural = 'PACI - Historia/Receta por paciente'

    def __str__(self):
        return f'{self.idpacientehistoria.idpaciente.nombre}, {self.observaciones}'