from django.db import models
from django.utils import timezone
from ..universal import AuditModel, TenantModel

class Sesion(AuditModel, TenantModel):
    """Registro y control de sesiones de usuarios"""
    
    idusuario = models.ForeignKey('Usuario', on_delete=models.CASCADE)
    
    # Información de la sesión
    token = models.CharField(max_length=255, unique=True)
    fecha_inicio = models.DateTimeField(default=timezone.now)
    fecha_ultimo_uso = models.DateTimeField(default=timezone.now)
    fecha_expiracion = models.DateTimeField()
    
    # Información del dispositivo/navegador
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, null=True)
    dispositivo = models.CharField(max_length=100, blank=True, null=True)
    navegador = models.CharField(max_length=50, blank=True, null=True)
    
    # Estados
    activa = models.BooleanField(default=True)
    cerrada_por_usuario = models.BooleanField(default=False)
    cerrada_por_inactividad = models.BooleanField(default=False)
    cerrada_por_admin = models.BooleanField(default=False)
    
    # Actividad
    paginas_visitadas = models.IntegerField(default=0)
    acciones_realizadas = models.IntegerField(default=0)
    ultima_accion = models.CharField(max_length=200, blank=True, null=True)
    
    class Meta:
        verbose_name = 'Sesión'
        verbose_name_plural = 'AUTH - Sesiones'
        ordering = ['-fecha_inicio']
    
    def __str__(self):
        return f"{self.idusuario.get_full_name()} - {self.fecha_inicio.strftime('%Y-%m-%d %H:%M')}"
    
    def esta_activa(self):
        """Verifica si la sesión está activa"""
        if not self.activa:
            return False
        
        if timezone.now() > self.fecha_expiracion:
            self.cerrar_por_expiracion()
            return False
        
        return True
    
    def cerrar_sesion(self, motivo='usuario'):
        """Cierra la sesión"""
        self.activa = False
        
        if motivo == 'usuario':
            self.cerrada_por_usuario = True
        elif motivo == 'inactividad':
            self.cerrada_por_inactividad = True
        elif motivo == 'admin':
            self.cerrada_por_admin = True
        
        self.save()
    
    def cerrar_por_expiracion(self):
        """Cierra la sesión por expiración"""
        self.cerrar_sesion('inactividad')
    
    def extender_sesion(self, minutos=60):
        """Extiende la duración de la sesión"""
        self.fecha_expiracion = timezone.now() + timezone.timedelta(minutes=minutos)
        self.fecha_ultimo_uso = timezone.now()
        self.save()
    
    def registrar_actividad(self, accion=''):
        """Registra actividad en la sesión"""
        self.fecha_ultimo_uso = timezone.now()
        self.acciones_realizadas += 1
        
        if accion:
            self.ultima_accion = accion
        
        # Auto-extender sesión con actividad
        if self.fecha_expiracion - timezone.now() < timezone.timedelta(minutes=15):
            self.extender_sesion()
        
        self.save()
    
    def get_duracion(self):
        """Obtiene la duración total de la sesión"""
        fecha_fin = self.fecha_ultimo_uso if not self.activa else timezone.now()
        return fecha_fin - self.fecha_inicio
    
    def get_tiempo_inactividad(self):
        """Obtiene el tiempo de inactividad actual"""
        if not self.activa:
            return None
        return timezone.now() - self.fecha_ultimo_uso
    
    def es_sospechosa(self):
        """Determina si la sesión es sospechosa"""
        # Criterios de sesión sospechosa
        criterios_sospechosos = []
        
        # Sesión muy larga (más de 12 horas)
        if self.get_duracion() > timezone.timedelta(hours=12):
            criterios_sospechosos.append('duracion_excesiva')
        
        # Muchas acciones por minuto
        duracion_minutos = max(self.get_duracion().total_seconds() / 60, 1)
        acciones_por_minuto = self.acciones_realizadas / duracion_minutos
        if acciones_por_minuto > 10:
            criterios_sospechosos.append('actividad_excesiva')
        
        # IP diferente a sesiones anteriores del usuario
        sesiones_anteriores = Sesion.objects.filter(
            idusuario=self.idusuario,
            fecha_inicio__lt=self.fecha_inicio
        ).values_list('ip_address', flat=True).distinct()
        
        if sesiones_anteriores and self.ip_address not in sesiones_anteriores:
            criterios_sospechosos.append('ip_nueva')
        
        return criterios_sospechosos
    
    @classmethod
    def limpiar_sesiones_expiradas(cls):
        """Limpia sesiones expiradas"""
        expiradas = cls.objects.filter(
            fecha_expiracion__lt=timezone.now(),
            activa=True
        )
        cantidad = expiradas.count()
        
        for sesion in expiradas:
            sesion.cerrar_por_expiracion()
        
        return cantidad
    
    @classmethod
    def get_sesiones_activas_usuario(cls, usuario):
        """Obtiene sesiones activas de un usuario"""
        return cls.objects.filter(
            idusuario=usuario,
            activa=True,
            fecha_expiracion__gt=timezone.now()
        )
    
    @classmethod
    def cerrar_todas_sesiones_usuario(cls, usuario, motivo='admin'):
        """Cierra todas las sesiones de un usuario"""
        sesiones_activas = cls.get_sesiones_activas_usuario(usuario)
        for sesion in sesiones_activas:
            sesion.cerrar_sesion(motivo)
        return sesiones_activas.count()