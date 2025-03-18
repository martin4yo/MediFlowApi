from django.db import models
from ..universal import AuditModel, TenantModel

class PacienteEmail(AuditModel, TenantModel):
    """ Clase para manejar los datos de paises """
    idpaciente = models.ForeignKey('Paciente', on_delete=models.CASCADE)
    email = models.CharField(max_length=200)

    class Meta:
        verbose_name = 'Email por Paciente'
        verbose_name_plural = 'PACI - Emails por paciente'

    def __str__(self):
        return f'{self.idpaciente.nombre}, {self.email}'