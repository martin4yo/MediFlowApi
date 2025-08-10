from django.db import models
from django.utils import timezone
from ..universal import AuditModel, TenantModel

class GastoAdministrativo(AuditModel, TenantModel):
    """Gastos administrativos del centro"""
    
    # Relación con centro
    idcentro = models.ForeignKey('Centro', on_delete=models.CASCADE)
    
    # Información del gasto
    categoria = models.CharField(max_length=30, choices=[
        ('SERVICIOS', 'Servicios (luz, gas, agua, internet)'),
        ('ALQUILER', 'Alquiler'),
        ('EQUIPAMIENTO', 'Equipamiento médico'),
        ('MANTENIMIENTO', 'Mantenimiento'),
        ('PERSONAL', 'Personal administrativo'),
        ('IMPUESTOS', 'Impuestos y tasas'),
        ('SEGUROS', 'Seguros'),
        ('MARKETING', 'Marketing y publicidad'),
        ('CAPACITACION', 'Capacitación'),
        ('MATERIALES', 'Materiales e insumos'),
        ('LIMPIEZA', 'Limpieza'),
        ('SISTEMAS', 'Sistemas y software'),
        ('OTRO', 'Otro')
    ])
    
    subcategoria = models.CharField(max_length=100, blank=True, null=True, help_text="Subcategoría específica del gasto")
    
    # Detalles del gasto
    concepto = models.CharField(max_length=200, help_text="Descripción del gasto")
    proveedor = models.CharField(max_length=200, blank=True, null=True)
    
    # Montos
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    iva = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="IVA del gasto")
    total = models.DecimalField(max_digits=10, decimal_places=2, help_text="Monto total con IVA")
    
    # Fechas
    fecha_gasto = models.DateField(help_text="Fecha en que se realizó el gasto")
    fecha_vencimiento = models.DateField(blank=True, null=True, help_text="Fecha de vencimiento si aplica")
    
    # Control de pago
    estado_pago = models.CharField(max_length=20, choices=[
        ('PENDIENTE', 'Pendiente de pago'),
        ('PAGADO', 'Pagado'),
        ('VENCIDO', 'Vencido'),
        ('ANULADO', 'Anulado')
    ], default='PENDIENTE')
    
    fecha_pago = models.DateField(blank=True, null=True)
    metodo_pago = models.CharField(max_length=20, choices=[
        ('EFECTIVO', 'Efectivo'),
        ('TRANSFERENCIA', 'Transferencia'),
        ('CHEQUE', 'Cheque'),
        ('TARJETA', 'Tarjeta'),
        ('DEBITO_AUTOMATICO', 'Débito Automático'),
        ('OTRO', 'Otro')
    ], blank=True, null=True)
    
    # Documentación
    numero_factura = models.CharField(max_length=50, blank=True, null=True)
    numero_recibo = models.CharField(max_length=50, blank=True, null=True)
    archivo_adjunto = models.CharField(max_length=255, blank=True, null=True, help_text="Ruta al archivo adjunto")
    
    # Información adicional
    es_recurrente = models.BooleanField(default=False, help_text="Indica si es un gasto recurrente mensual")
    observaciones = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Gasto Administrativo'
        verbose_name_plural = 'FIN - Gastos Administrativos'
        ordering = ['-fecha_gasto']
        
    def save(self, *args, **kwargs):
        # Calcular total si no está establecido
        if not self.total:
            self.total = self.monto + self.iva
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f'{self.concepto} - ${self.total} - {self.fecha_gasto}'
    
    def marcar_pagado(self, fecha_pago=None, metodo_pago=None):
        """Marca el gasto como pagado"""
        self.estado_pago = 'PAGADO'
        self.fecha_pago = fecha_pago or timezone.now().date()
        if metodo_pago:
            self.metodo_pago = metodo_pago
        self.save()
    
    def esta_vencido(self):
        """Verifica si el gasto está vencido"""
        if self.fecha_vencimiento and self.estado_pago == 'PENDIENTE':
            return timezone.now().date() > self.fecha_vencimiento
        return False
    
    @property
    def dias_vencimiento(self):
        """Días hasta el vencimiento o días vencido"""
        if self.fecha_vencimiento:
            delta = (self.fecha_vencimiento - timezone.now().date()).days
            return delta
        return None