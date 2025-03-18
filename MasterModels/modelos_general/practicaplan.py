from django.db import models
from ..universal import AuditModel, TenantModel

class PracticaPlan(AuditModel, TenantModel):
    """ Clase para manejar los datos de paises """
    idespecialidadpractica = models.ForeignKey('EspecialidadPractica', on_delete=models.CASCADE)
    idcoberturaplan = models.ForeignKey('CoberturaPlan', on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = 'Practica por Plan'
        verbose_name_plural = 'GRAL - Practicas por Plan'

    def __str__(self):
        return f'{self.idcoberturaplan.nombre}, {self.idespecialidadpractica.idpractica.nombre}'