from django.db import models
from django.utils import timezone
from ..universal import AuditModel, TenantModel

class Pago(AuditModel, TenantModel):
    """Pagos realizados por pacientes"""
    
    # Relaciones
    idturno = models.ForeignKey('Turno', on_delete=models.CASCADE)
    idpaciente = models.ForeignKey('Paciente', on_delete=models.CASCADE)
    idcentro = models.ForeignKey('Centro', on_delete=models.CASCADE)
    
    # Información del pago
    tipo_pago = models.CharField(max_length=20, choices=[
        ('SENA', 'Seña'),
        ('RESTO', 'Resto'),
        ('COMPLETO', 'Pago Completo'),
        ('REEMBOLSO', 'Reembolso')
    ])
    
    metodo_pago = models.CharField(max_length=20, choices=[
        ('EFECTIVO', 'Efectivo'),
        ('TARJETA_DEBITO', 'Tarjeta de Débito'),
        ('TARJETA_CREDITO', 'Tarjeta de Crédito'),
        ('TRANSFERENCIA', 'Transferencia'),
        ('MERCADOPAGO', 'Mercado Pago'),
        ('OTRO', 'Otro')
    ])
    
    # Montos
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    monto_cobertura = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Monto que cubre la obra social")
    monto_paciente = models.DecimalField(max_digits=10, decimal_places=2, help_text="Monto que paga el paciente")
    
    # Control
    fecha_pago = models.DateTimeField(default=timezone.now)
    comprobante = models.CharField(max_length=100, blank=True, null=True, help_text="Número de comprobante/recibo")
    observaciones = models.TextField(blank=True, null=True)
    
    # Estado
    estado_pago = models.CharField(max_length=20, choices=[
        ('PENDIENTE', 'Pendiente'),
        ('PROCESADO', 'Procesado'),
        ('CONFIRMADO', 'Confirmado'),
        ('ANULADO', 'Anulado')
    ], default='PROCESADO')
    
    class Meta:
        verbose_name = 'Pago'
        verbose_name_plural = 'FIN - Pagos'
        
    def __str__(self):
        return f'{self.idpaciente.apellido} - ${self.monto} - {self.tipo_pago}'
    
    @property
    def es_sena(self):
        return self.tipo_pago == 'SENA'
    
    @property
    def requiere_resto(self):
        """Verifica si este pago es una seña y requiere el pago del resto"""
        if self.tipo_pago == 'SENA':
            # Verificar si ya existe el pago del resto
            return not Pago.objects.filter(
                idturno=self.idturno,
                tipo_pago='RESTO',
                estado_pago__in=['PROCESADO', 'CONFIRMADO']
            ).exists()
        return False