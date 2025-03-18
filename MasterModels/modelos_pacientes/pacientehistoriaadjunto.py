from django.db import models
from ..universal import AuditModel, TenantModel

class PacienteHistoriaAdjunto(AuditModel, TenantModel):
    """ Clase para manejar los datos de paises """
    idpacientehistoria = models.ForeignKey('PacienteHistoria', on_delete=models.CASCADE)
    documento = models.FileField(upload_to='documentos_pacientes')
    documenttype = models.CharField(max_length=200)
    observaciones = models.CharField(max_length=200)
    
    class Meta:
        verbose_name = 'Historia Adjuntos'
        verbose_name_plural = 'PACI - Historia/Adjuntos por paciente'

    def __str__(self):
        return f'{self.idpacientehistoria.idpaciente.nombre}, {self.observaciones}'