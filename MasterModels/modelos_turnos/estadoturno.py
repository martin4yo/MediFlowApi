from django.db import models
from ..universal import AuditModel, TenantModel

class EstadoTurno(AuditModel, TenantModel):
    """Estados posibles para un turno"""
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=7, default='#6B7280')  # Color hex para UI
    
    # Estados predefinidos: SOLICITADO, CONFIRMADO, EN_ESPERA, EN_ATENCION, ATENDIDO, CANCELADO, NO_ASISTIO
    
    class Meta:
        verbose_name = 'Estado de Turno'
        verbose_name_plural = 'TURN - Estados de Turno'
        
    def __str__(self):
        return f'{self.codigo} - {self.nombre}'