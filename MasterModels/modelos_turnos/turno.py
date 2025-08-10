from django.db import models
from django.utils import timezone
from ..universal import AuditModel, TenantModel

class Turno(AuditModel, TenantModel):
    """Turnos solicitados por pacientes"""
    # Relaciones principales
    idpaciente = models.ForeignKey('Paciente', on_delete=models.CASCADE)
    idprofesional = models.ForeignKey('Profesional', on_delete=models.CASCADE)
    idcentro = models.ForeignKey('Centro', on_delete=models.CASCADE)
    idespecialidadpractica = models.ForeignKey('EspecialidadPractica', on_delete=models.CASCADE)
    idestadoturno = models.ForeignKey('EstadoTurno', on_delete=models.CASCADE)
    
    # Información del turno
    fecha = models.DateField()
    hora = models.TimeField()
    duracion_minutos = models.IntegerField(default=30)
    
    # Información adicional
    observaciones_paciente = models.TextField(blank=True, null=True)
    observaciones_recepcion = models.TextField(blank=True, null=True)
    observaciones_profesional = models.TextField(blank=True, null=True)
    
    # Información de cobertura
    idcobertura = models.ForeignKey('Cobertura', on_delete=models.SET_NULL, blank=True, null=True)
    es_particular = models.BooleanField(default=False)
    cobra_profesional = models.BooleanField(default=False)  # Si es particular, indica si cobra el profesional
    
    # Timestamps importantes
    fecha_solicitud = models.DateTimeField(default=timezone.now)
    fecha_confirmacion = models.DateTimeField(blank=True, null=True)
    fecha_llegada = models.DateTimeField(blank=True, null=True)
    fecha_inicio_atencion = models.DateTimeField(blank=True, null=True)
    fecha_fin_atencion = models.DateTimeField(blank=True, null=True)
    fecha_cancelacion = models.DateTimeField(blank=True, null=True)
    
    # Control de recordatorios
    recordatorio_enviado = models.BooleanField(default=False)
    fecha_recordatorio = models.DateTimeField(blank=True, null=True)
    
    # Información de precios
    precio_total = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Precio total del turno")
    precio_cobertura = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Parte cubierta por obra social")
    precio_paciente = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Parte que paga el paciente")
    
    # Control de pagos
    sena_requerida = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Monto de seña requerida")
    sena_pagada = models.BooleanField(default=False)
    pago_completo = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Turno'
        verbose_name_plural = 'TURN - Turnos'
        unique_together = ['idprofesional', 'idcentro', 'fecha', 'hora']
        
    def __str__(self):
        return f'{self.idpaciente.apellido} - {self.idprofesional.apellido} - {self.fecha} {self.hora}'
    
    @property
    def fecha_hora(self):
        """Combina fecha y hora en un datetime"""
        return timezone.datetime.combine(self.fecha, self.hora)
    
    @property
    def puede_cancelar(self):
        """Verifica si el turno puede ser cancelado"""
        return self.idestadoturno.codigo in ['SOLICITADO', 'CONFIRMADO', 'EN_ESPERA']
    
    @property
    def requiere_preparacion(self):
        """Verifica si la práctica requiere preparación previa"""
        return bool(self.idespecialidadpractica.idpractica.preparacion)
    
    @property
    def saldo_pendiente(self):
        """Calcula el saldo pendiente de pago"""
        from MasterModels.modelos_financieros.pago import Pago
        
        # Sumar todos los pagos confirmados para este turno
        pagos_realizados = Pago.objects.filter(
            idturno=self,
            estado_pago__in=['PROCESADO', 'CONFIRMADO']
        ).exclude(tipo_pago='REEMBOLSO').aggregate(
            total=models.Sum('monto')
        )['total'] or 0
        
        return self.precio_paciente - pagos_realizados
    
    @property
    def requiere_sena(self):
        """Verifica si el turno requiere seña"""
        return self.sena_requerida > 0 and not self.sena_pagada
    
    def calcular_precios(self):
        """Calcula los precios basándose en la configuración de la práctica y cobertura"""
        # Precio base de la práctica
        precio_base = getattr(self.idespecialidadpractica.idpractica, 'precio_base', 0)
        
        if precio_base == 0:
            # Si no hay precio configurado, usar un precio por defecto o configuración del centro
            precio_base = 5000  # Precio por defecto, esto debería venir de configuración
        
        self.precio_total = precio_base
        
        # Calcular cobertura si aplica
        if self.idcobertura and not self.es_particular:
            # Aquí se podría consultar el plan de cobertura para ver qué porcentaje cubre
            self.precio_cobertura = precio_base * 0.7  # 70% por defecto
            self.precio_paciente = precio_base - self.precio_cobertura
        else:
            self.precio_cobertura = 0
            self.precio_paciente = precio_base
        
        # Configurar seña (por ejemplo, 30% del precio del paciente)
        if self.precio_paciente > 2000:  # Solo si el monto es significativo
            self.sena_requerida = self.precio_paciente * 0.3
        
        self.save()
    
    def marcar_sena_pagada(self):
        """Marca la seña como pagada"""
        self.sena_pagada = True
        self.save()
    
    def marcar_pago_completo(self):
        """Marca el pago como completo"""
        self.pago_completo = True
        self.save()