from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from ..universal import AuditModel, TenantModel

class ConfiguracionComision(AuditModel, TenantModel):
    """Configuración de comisiones por profesional, centro y práctica"""
    
    # Relaciones - todas opcionales para permitir configuraciones generales
    idprofesional = models.ForeignKey('Profesional', on_delete=models.CASCADE, blank=True, null=True)
    idcentro = models.ForeignKey('Centro', on_delete=models.CASCADE, blank=True, null=True)
    idespecialidadpractica = models.ForeignKey('EspecialidadPractica', on_delete=models.CASCADE, blank=True, null=True)
    
    # Configuración de comisiones (en porcentajes)
    porcentaje_profesional = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Porcentaje que se lleva el profesional (0-100)"
    )
    porcentaje_centro = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Porcentaje que se lleva el centro (0-100)"
    )
    
    # Prioridad para resolver conflictos (1 = mayor prioridad)
    prioridad = models.IntegerField(default=5, help_text="1=Específico (Prof+Centro+Práctica), 5=General")
    
    # Vigencia
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    
    # Información adicional
    descripcion = models.CharField(max_length=200, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Configuración de Comisión'
        verbose_name_plural = 'FIN - Configuraciones de Comisión'
        ordering = ['prioridad', '-fecha_inicio']
        
    def clean(self):
        """Validar que los porcentajes sumen 100"""
        from django.core.exceptions import ValidationError
        if self.porcentaje_profesional + self.porcentaje_centro != 100:
            raise ValidationError(
                'La suma de porcentaje_profesional y porcentaje_centro debe ser 100'
            )
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        
    def __str__(self):
        elementos = []
        if self.idprofesional:
            elementos.append(f"Prof: {self.idprofesional.apellido}")
        if self.idcentro:
            elementos.append(f"Centro: {self.idcentro.codigo}")
        if self.idespecialidadpractica:
            elementos.append(f"Práctica: {self.idespecialidadpractica.idpractica.nombre}")
        
        detalle = " - ".join(elementos) if elementos else "General"
        return f'{detalle} ({self.porcentaje_profesional}%/{self.porcentaje_centro}%)'
    
    @classmethod
    def obtener_comision(cls, profesional, centro, especialidad_practica, fecha=None):
        """
        Obtiene la configuración de comisión más específica para los parámetros dados
        """
        from django.utils import timezone
        
        if fecha is None:
            fecha = timezone.now().date()
        
        # Buscar configuraciones aplicables ordenadas por prioridad (más específica primero)
        configuraciones = cls.objects.filter(
            activo=True,
            fecha_inicio__lte=fecha
        ).filter(
            models.Q(fecha_fin__isnull=True) | models.Q(fecha_fin__gte=fecha)
        ).filter(
            # Debe coincidir o ser None (configuración general)
            models.Q(idprofesional__isnull=True) | models.Q(idprofesional=profesional)
        ).filter(
            models.Q(idcentro__isnull=True) | models.Q(idcentro=centro)
        ).filter(
            models.Q(idespecialidadpractica__isnull=True) | models.Q(idespecialidadpractica=especialidad_practica)
        ).order_by('prioridad')
        
        return configuraciones.first()