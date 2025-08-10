from django.db import models
from django.core.exceptions import ValidationError
from ..universal import AuditModel, TenantModel

class Centro(AuditModel):
    """ Clase para manejar los centros médicos """
    
    # Relación con tenant (temporal nullable para migración)
    tenant = models.ForeignKey(
        'MasterModels.Tenant',
        on_delete=models.CASCADE,
        related_name='centros',
        verbose_name="Tenant",
        help_text="Tenant al que pertenece este centro",
        null=True,
        blank=True
    )
    
    codigo = models.CharField(max_length=10, default='')
    nombre = models.CharField(max_length=200)
    direccion = models.CharField(max_length=200, blank=True, null=True)
    localidad = models.CharField(max_length=200, blank=True, null=True)
    telefono = models.CharField(max_length=200, blank=True, null=True)
    horario = models.CharField(max_length=200, blank=True, null=True)
    mail = models.EmailField(max_length=200, blank=True, null=True)
    web = models.CharField(max_length=200, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    
    # Campo adicional para el estado
    activo = models.BooleanField(
        default=True,
        verbose_name="Activo",
        help_text="Si el centro está activo"
    )
    

    class Meta:
        verbose_name = 'Centro'
        verbose_name_plural = 'GRAL - Centros'
        unique_together = [('tenant', 'codigo')]  # Código único por tenant
        ordering = ['tenant', 'nombre']

    def __str__(self):
        return f'{self.tenant.codigo}-{self.codigo}: {self.nombre}'
    
    def save(self, *args, **kwargs):
        # Validar límites del tenant antes de guardar
        if not self.pk and self.tenant and not self.tenant.puede_agregar_centros:
            raise ValidationError(f"El tenant {self.tenant.nombre} ha alcanzado su límite de centros ({self.tenant.limite_centros})")
        super().save(*args, **kwargs) 
    
