from django.db import models
from django.utils import timezone
from django.db.models import Sum
from ..universal import AuditModel, TenantModel

class Liquidacion(AuditModel, TenantModel):
    """Liquidaciones de comisiones a profesionales"""
    
    # Relaciones
    idprofesional = models.ForeignKey('Profesional', on_delete=models.CASCADE)
    idcentro = models.ForeignKey('Centro', on_delete=models.CASCADE)
    
    # Período de liquidación
    periodo_desde = models.DateField()
    periodo_hasta = models.DateField()
    
    # Montos
    total_bruto = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Total de ingresos del período")
    total_comision_profesional = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Total de comisión del profesional")
    total_comision_centro = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Total de comisión del centro")
    
    # Descuentos/Ajustes
    descuentos = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Descuentos aplicados")
    ajustes = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Ajustes (pueden ser negativos)")
    
    # Total a pagar
    total_a_pagar = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Total final a pagar al profesional")
    
    # Estado
    estado = models.CharField(max_length=20, choices=[
        ('BORRADOR', 'Borrador'),
        ('CALCULADA', 'Calculada'),
        ('APROBADA', 'Aprobada'),
        ('PAGADA', 'Pagada'),
        ('ANULADA', 'Anulada')
    ], default='BORRADOR')
    
    # Control
    fecha_calculo = models.DateTimeField(blank=True, null=True)
    fecha_aprobacion = models.DateTimeField(blank=True, null=True)
    fecha_pago = models.DateTimeField(blank=True, null=True)
    
    # Información adicional
    numero_liquidacion = models.CharField(max_length=50, unique=True, blank=True)
    observaciones = models.TextField(blank=True, null=True)
    detalle_calculo = models.JSONField(default=dict, blank=True, help_text="Detalle del cálculo por práctica/turno")
    
    class Meta:
        verbose_name = 'Liquidación'
        verbose_name_plural = 'FIN - Liquidaciones'
        unique_together = ['idprofesional', 'idcentro', 'periodo_desde', 'periodo_hasta']
        
    def save(self, *args, **kwargs):
        if not self.numero_liquidacion:
            self.generar_numero_liquidacion()
        super().save(*args, **kwargs)
    
    def generar_numero_liquidacion(self):
        """Genera un número único de liquidación"""
        import datetime
        now = timezone.now()
        base = f"LIQ-{self.idprofesional.id}-{self.idcentro.id}-{now.strftime('%Y%m%d')}"
        
        # Buscar el último número para evitar duplicados
        count = Liquidacion.objects.filter(numero_liquidacion__startswith=base).count()
        self.numero_liquidacion = f"{base}-{count + 1:03d}"
    
    def __str__(self):
        return f'{self.numero_liquidacion} - {self.idprofesional.apellido} - ${self.total_a_pagar}'
    
    def calcular_liquidacion(self):
        """Calcula los montos de la liquidación basándose en los pagos del período"""
        from .pago import Pago
        from .configuracioncomision import ConfiguracionComision
        
        # Obtener todos los pagos del período para este profesional y centro
        pagos = Pago.objects.filter(
            idturno__idprofesional=self.idprofesional,
            idturno__idcentro=self.idcentro,
            fecha_pago__date__gte=self.periodo_desde,
            fecha_pago__date__lte=self.periodo_hasta,
            estado_pago__in=['PROCESADO', 'CONFIRMADO']
        ).exclude(tipo_pago='REEMBOLSO')
        
        total_bruto = 0
        total_comision_profesional = 0
        total_comision_centro = 0
        detalle = {}
        
        for pago in pagos:
            # Obtener configuración de comisión
            config = ConfiguracionComision.obtener_comision(
                self.idprofesional,
                self.idcentro,
                pago.idturno.idespecialidadpractica,
                pago.fecha_pago.date()
            )
            
            if config:
                monto = pago.monto
                comision_prof = monto * (config.porcentaje_profesional / 100)
                comision_centro = monto * (config.porcentaje_centro / 100)
            else:
                # Configuración por defecto si no hay configuración específica
                monto = pago.monto
                comision_prof = monto * 0.70  # 70% profesional por defecto
                comision_centro = monto * 0.30  # 30% centro por defecto
            
            total_bruto += monto
            total_comision_profesional += comision_prof
            total_comision_centro += comision_centro
            
            # Agregar al detalle
            key = f"pago_{pago.id}"
            detalle[key] = {
                'pago_id': pago.id,
                'fecha': pago.fecha_pago.isoformat(),
                'monto': float(monto),
                'comision_profesional': float(comision_prof),
                'comision_centro': float(comision_centro),
                'paciente': pago.idpaciente.nombre_completo if hasattr(pago.idpaciente, 'nombre_completo') else str(pago.idpaciente),
                'practica': pago.idturno.idespecialidadpractica.idpractica.nombre
            }
        
        # Actualizar campos
        self.total_bruto = total_bruto
        self.total_comision_profesional = total_comision_profesional
        self.total_comision_centro = total_comision_centro
        self.total_a_pagar = total_comision_profesional - self.descuentos + self.ajustes
        self.detalle_calculo = detalle
        self.fecha_calculo = timezone.now()
        self.estado = 'CALCULADA'
        
        self.save()
        
    def aprobar(self):
        """Aprueba la liquidación"""
        if self.estado == 'CALCULADA':
            self.estado = 'APROBADA'
            self.fecha_aprobacion = timezone.now()
            self.save()
    
    def marcar_pagada(self):
        """Marca la liquidación como pagada"""
        if self.estado == 'APROBADA':
            self.estado = 'PAGADA'
            self.fecha_pago = timezone.now()
            self.save()