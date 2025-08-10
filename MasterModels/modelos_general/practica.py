from django.db import models
from ..universal import AuditModel, TenantModel

class Practica(AuditModel, TenantModel):
    """ Clase para manejar las prácticas médicas """
    codigo = models.CharField(max_length=10, default='', unique=True)
    nombre = models.CharField(max_length=200)
    preparacion = models.TextField(blank=True, null=True, help_text="Instrucciones de preparación previa (ayuno, requisitos, etc.)")
    duracion_estimada_minutos = models.IntegerField(default=30, help_text="Duración estimada en minutos")
    precio_base = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Precio base de la práctica")
    
    class Meta:
        verbose_name = 'Practica'
        verbose_name_plural = 'GRAL - Practicas'

    def __str__(self):
        return f'{self.codigo}, {self.nombre}'