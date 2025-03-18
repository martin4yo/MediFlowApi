from django.db import models
from ..universal import AuditModel, TenantModel

class ProfesionalDocumento(AuditModel, TenantModel):
    """ Clase para manejar los datos de paises """
    idprofesional = models.ForeignKey('Profesional', on_delete=models.CASCADE)
    iddocumento = models.ForeignKey('Documento', on_delete=models.CASCADE)
    numero = models.CharField(max_length=200)
    vigencia = models.DateField()

    class Meta:
        verbose_name = 'Documentos por Profesional'
        verbose_name_plural = 'PROS - Documentos por Profesional'

    def __str__(self):
        return f'{self.idprofesional.prefijo}, {self.idprofesional.apellido}, {self.iddocumento.nombre}, {self.numero}, {self.vigencia}'