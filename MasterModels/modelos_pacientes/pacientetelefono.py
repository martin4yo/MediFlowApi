from django.db import models
from ..universal import AuditModel, TenantModel

class PacienteTelefono(AuditModel, TenantModel):
    """ Clase para manejar los datos de paises """
    idpaciente = models.ForeignKey('Paciente', on_delete=models.CASCADE)
    telefono = models.CharField(max_length=200)

    class Meta:
        verbose_name = 'Telefono por Paciente'
        verbose_name_plural = 'PACI - Telefonos por paciente'

    def __str__(self):
        return f'{self.idpaciente.nombre}, {self.telefono}'