from django.db import models
from ..universal import AuditModel, TenantModel

class ProfesionalTelefono(AuditModel, TenantModel):
    """ Clase para manejar los datos de paises """
    idprofesional = models.ForeignKey('Profesional', on_delete=models.CASCADE)  
    telefono = models.CharField(max_length=200)
    publico = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Telefono por Profesional'
        verbose_name_plural = 'PROS - Telefonos por profesional'

    def __str__(self):
        return f'{self.idprofesional.nombre}, {self.telefono}, {self.publico}'