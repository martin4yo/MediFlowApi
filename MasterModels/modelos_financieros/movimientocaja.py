from django.db import models
from django.utils import timezone
from ..universal import AuditModel, TenantModel

class MovimientoCaja(AuditModel, TenantModel):
    """Registro de movimientos de caja (ingresos y egresos)"""
    
    # Relación con centro
    idcentro = models.ForeignKey('Centro', on_delete=models.CASCADE)
    
    # Tipo de movimiento
    tipo_movimiento = models.CharField(max_length=10, choices=[
        ('INGRESO', 'Ingreso'),
        ('EGRESO', 'Egreso')
    ])
    
    # Categoría del movimiento
    categoria = models.CharField(max_length=30, choices=[
        # INGRESOS
        ('CONSULTA', 'Pago de consulta'),
        ('SENA', 'Seña de turno'),
        ('COBERTURA', 'Pago de cobertura'),
        ('OTRO_INGRESO', 'Otro ingreso'),
        
        # EGRESOS
        ('LIQUIDACION', 'Liquidación a profesional'),
        ('GASTO_ADMIN', 'Gasto administrativo'),
        ('SERVICIOS', 'Servicios'),
        ('IMPUESTOS', 'Impuestos'),
        ('EQUIPAMIENTO', 'Equipamiento'),
        ('OTRO_EGRESO', 'Otro egreso')
    ])
    
    # Detalles del movimiento
    concepto = models.CharField(max_length=200, help_text="Descripción del movimiento")
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Referencias a otros modelos
    idpago = models.ForeignKey('Pago', on_delete=models.SET_NULL, blank=True, null=True, help_text="Referencia al pago si aplica")
    idliquidacion = models.ForeignKey('Liquidacion', on_delete=models.SET_NULL, blank=True, null=True, help_text="Referencia a liquidación si aplica")
    idgastoadministrativo = models.ForeignKey('GastoAdministrativo', on_delete=models.SET_NULL, blank=True, null=True, help_text="Referencia al gasto si aplica")
    
    # Control temporal
    fecha_movimiento = models.DateTimeField(default=timezone.now)
    
    # Método de pago/cobro
    metodo = models.CharField(max_length=20, choices=[
        ('EFECTIVO', 'Efectivo'),
        ('TRANSFERENCIA', 'Transferencia'),
        ('CHEQUE', 'Cheque'),
        ('TARJETA_DEBITO', 'Tarjeta de Débito'),
        ('TARJETA_CREDITO', 'Tarjeta de Crédito'),
        ('MERCADOPAGO', 'Mercado Pago'),
        ('OTRO', 'Otro')
    ])
    
    # Control de caja
    saldo_anterior = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    saldo_posterior = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Usuario responsable
    usuario_responsable = models.ForeignKey('Persona', on_delete=models.SET_NULL, blank=True, null=True, related_name='movimientos_responsable')
    
    # Información adicional
    comprobante = models.CharField(max_length=100, blank=True, null=True, help_text="Número de comprobante")
    observaciones = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Movimiento de Caja'
        verbose_name_plural = 'FIN - Movimientos de Caja'
        ordering = ['-fecha_movimiento']
        
    def save(self, *args, **kwargs):
        # Calcular saldo posterior
        if not self.saldo_posterior:
            if self.tipo_movimiento == 'INGRESO':
                self.saldo_posterior = self.saldo_anterior + self.monto
            else:  # EGRESO
                self.saldo_posterior = self.saldo_anterior - self.monto
        super().save(*args, **kwargs)
        
    def __str__(self):
        signo = '+' if self.tipo_movimiento == 'INGRESO' else '-'
        return f'{self.fecha_movimiento.strftime("%d/%m/%Y")} - {signo}${self.monto} - {self.concepto}'
    
    @classmethod
    def calcular_saldo_actual(cls, centro_id, fecha_hasta=None):
        """Calcula el saldo actual de caja para un centro"""
        from django.db.models import Sum
        
        filtros = {'idcentro_id': centro_id}
        if fecha_hasta:
            filtros['fecha_movimiento__lte'] = fecha_hasta
        
        # Sumar ingresos
        ingresos = cls.objects.filter(
            tipo_movimiento='INGRESO',
            **filtros
        ).aggregate(total=Sum('monto'))['total'] or 0
        
        # Sumar egresos
        egresos = cls.objects.filter(
            tipo_movimiento='EGRESO',
            **filtros
        ).aggregate(total=Sum('monto'))['total'] or 0
        
        return ingresos - egresos
    
    @classmethod
    def crear_movimiento_desde_pago(cls, pago):
        """Crea un movimiento de caja desde un pago"""
        return cls.objects.create(
            idcentro=pago.idcentro,
            tipo_movimiento='INGRESO',
            categoria='CONSULTA' if pago.tipo_pago != 'SENA' else 'SENA',
            concepto=f'Pago {pago.tipo_pago.lower()} - {pago.idpaciente}',
            monto=pago.monto,
            idpago=pago,
            fecha_movimiento=pago.fecha_pago,
            metodo=pago.metodo_pago,
            comprobante=pago.comprobante,
            usuario_responsable=pago.user_id
        )
    
    @classmethod
    def crear_movimiento_desde_liquidacion(cls, liquidacion):
        """Crea un movimiento de caja desde una liquidación"""
        return cls.objects.create(
            idcentro=liquidacion.idcentro,
            tipo_movimiento='EGRESO',
            categoria='LIQUIDACION',
            concepto=f'Liquidación {liquidacion.numero_liquidacion} - {liquidacion.idprofesional}',
            monto=liquidacion.total_a_pagar,
            idliquidacion=liquidacion,
            fecha_movimiento=liquidacion.fecha_pago or timezone.now(),
            metodo='TRANSFERENCIA',  # Por defecto
            usuario_responsable=liquidacion.user_id
        )