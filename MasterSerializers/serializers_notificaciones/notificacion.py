from rest_framework import serializers
from MasterModels.modelos_notificaciones.notificacion import Notificacion
from MasterSerializers.serializers_pacientes.paciente import PacienteSerializer
from MasterSerializers.serializers_turnos.turno import TurnoSerializer
from MasterSerializers.serializers_general.centro import CentroSerializer

class NotificacionSerializer(serializers.ModelSerializer):
    # Displays
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    canal_display = serializers.CharField(source='get_canal_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    prioridad_display = serializers.CharField(source='get_prioridad_display', read_only=True)
    
    # Propiedades calculadas
    puede_reintentar = serializers.BooleanField(read_only=True)
    
    # Relaciones anidadas (opcional)
    paciente_info = PacienteSerializer(source='idpaciente', read_only=True)
    turno_info = TurnoSerializer(source='idturno', read_only=True)
    centro_info = CentroSerializer(source='idcentro', read_only=True)
    
    class Meta:
        model = Notificacion
        fields = [
            'id', 'destinatario_email', 'destinatario_telefono', 'destinatario_nombre',
            'idpaciente', 'idturno', 'idcentro', 'tipo', 'tipo_display', 
            'canal', 'canal_display', 'asunto', 'contenido', 'estado', 'estado_display',
            'fecha_programada', 'fecha_enviado', 'fecha_entregado', 'intentos', 
            'max_intentos', 'respuesta_externa', 'mensaje_error', 'prioridad', 
            'prioridad_display', 'puede_reintentar', 'paciente_info', 'turno_info', 
            'centro_info', 'created_at', 'updated_at', 'disabled'
        ]
        read_only_fields = ['fecha_enviado', 'fecha_entregado', 'intentos']

class NotificacionListSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    canal_display = serializers.CharField(source='get_canal_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    paciente_nombre = serializers.SerializerMethodField()
    
    class Meta:
        model = Notificacion
        fields = [
            'id', 'tipo', 'tipo_display', 'canal', 'canal_display', 
            'destinatario_nombre', 'paciente_nombre', 'asunto', 'estado', 
            'estado_display', 'fecha_programada', 'intentos', 'prioridad'
        ]
    
    def get_paciente_nombre(self, obj):
        if obj.idpaciente and hasattr(obj.idpaciente, 'persona'):
            return obj.idpaciente.persona.get_nombre_completo()
        return obj.destinatario_nombre

class NotificacionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacion
        fields = [
            'destinatario_email', 'destinatario_telefono', 'destinatario_nombre',
            'idpaciente', 'idturno', 'idcentro', 'tipo', 'canal', 'asunto', 
            'contenido', 'fecha_programada', 'prioridad', 'max_intentos'
        ]