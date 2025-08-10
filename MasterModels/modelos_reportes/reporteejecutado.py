from django.db import models
from django.utils import timezone
from ..universal import AuditModel, TenantModel

class ReporteEjecutado(AuditModel, TenantModel):
    """Historial de ejecuciones de reportes con resultados cacheados"""
    
    idreporte = models.ForeignKey('Reporte', on_delete=models.CASCADE)
    
    # Información de ejecución
    fecha_ejecucion = models.DateTimeField(default=timezone.now)
    usuario_ejecutor = models.CharField(max_length=100, help_text="Usuario que ejecutó el reporte")
    
    # Parámetros utilizados
    filtros_aplicados = models.JSONField(default=dict)
    
    # Resultados
    resultado_data = models.JSONField(default=dict, help_text="Datos del reporte en formato JSON")
    total_registros = models.IntegerField(default=0)
    
    # Metadatos de ejecución
    tiempo_ejecucion_ms = models.IntegerField(default=0, help_text="Tiempo de ejecución en milisegundos")
    estado = models.CharField(max_length=20, choices=[
        ('EXITOSO', 'Exitoso'),
        ('ERROR', 'Error'),
        ('CANCELADO', 'Cancelado')
    ], default='EXITOSO')
    
    mensaje_error = models.TextField(blank=True, null=True)
    
    # Control de cache
    valido_hasta = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Reporte Ejecutado'
        verbose_name_plural = 'REP - Reportes Ejecutados'
        ordering = ['-fecha_ejecucion']
    
    def __str__(self):
        return f'{self.idreporte.nombre} - {self.fecha_ejecucion.strftime("%Y-%m-%d %H:%M")}'
    
    def esta_vigente(self):
        """Verifica si el resultado cacheado aún está vigente"""
        if not self.valido_hasta:
            return False
        return timezone.now() <= self.valido_hasta
    
    def marcar_expirado(self):
        """Marca el cache como expirado"""
        self.valido_hasta = timezone.now()
        self.save()
    
    def get_resumen_estadistico(self):
        """Genera un resumen estadístico básico de los datos"""
        if not self.resultado_data.get('datos'):
            return {}
        
        datos = self.resultado_data['datos']
        
        return {
            'total_registros': len(datos),
            'fecha_generacion': self.fecha_ejecucion.isoformat(),
            'tiempo_ejecucion': f"{self.tiempo_ejecucion_ms}ms",
            'filtros_aplicados': self.filtros_aplicados
        }