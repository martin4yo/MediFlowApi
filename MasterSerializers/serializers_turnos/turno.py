from rest_framework import serializers
from MasterModels.modelos_turnos.turno import Turno
from MasterSerializers.serializers_pacientes.paciente import PacienteSerializer
from MasterSerializers.serializers_profesionales.profesional import ProfesionalSerializer
from MasterSerializers.serializers_general.centro import CentroSerializer
from MasterSerializers.serializers_general.especialidadpractica import EspecialidadPracticaSerializer
from MasterSerializers.serializers_general.cobertura import CoberturaSerializer
from .estadoturno import EstadoTurnoSerializer

class TurnoSerializer(serializers.ModelSerializer):
    paciente_nombre_completo = serializers.CharField(source='idpaciente.nombre_completo', read_only=True)
    profesional_nombre_completo = serializers.CharField(source='idprofesional.nombre_completo', read_only=True)
    centro_nombre = serializers.CharField(source='idcentro.nombre', read_only=True)
    especialidad_practica_nombre = serializers.CharField(source='idespecialidadpractica.idpractica.nombre', read_only=True)
    estado_nombre = serializers.CharField(source='idestadoturno.nombre', read_only=True)
    estado_color = serializers.CharField(source='idestadoturno.color', read_only=True)
    cobertura_nombre = serializers.CharField(source='idcobertura.nombre', read_only=True)
    
    # Propiedades calculadas
    fecha_hora = serializers.DateTimeField(read_only=True)
    puede_cancelar = serializers.BooleanField(read_only=True)
    requiere_preparacion = serializers.BooleanField(read_only=True)
    preparacion_texto = serializers.CharField(source='idespecialidadpractica.idpractica.preparacion', read_only=True)
    
    class Meta:
        model = Turno
        fields = [
            'id', 'idpaciente', 'idprofesional', 'idcentro', 'idespecialidadpractica',
            'idestadoturno', 'idcobertura', 'fecha', 'hora', 'duracion_minutos',
            'observaciones_paciente', 'observaciones_recepcion', 'observaciones_profesional',
            'es_particular', 'cobra_profesional', 'fecha_solicitud', 'fecha_confirmacion',
            'fecha_llegada', 'fecha_inicio_atencion', 'fecha_fin_atencion', 'fecha_cancelacion',
            'recordatorio_enviado', 'fecha_recordatorio',
            'paciente_nombre_completo', 'profesional_nombre_completo', 'centro_nombre',
            'especialidad_practica_nombre', 'estado_nombre', 'estado_color', 'cobertura_nombre',
            'fecha_hora', 'puede_cancelar', 'requiere_preparacion', 'preparacion_texto',
            'created_at', 'updated_at', 'disabled'
        ]

class TurnoDetailSerializer(TurnoSerializer):
    idpaciente = PacienteSerializer(read_only=True)
    idprofesional = ProfesionalSerializer(read_only=True)
    idcentro = CentroSerializer(read_only=True)
    idespecialidadpractica = EspecialidadPracticaSerializer(read_only=True)
    idestadoturno = EstadoTurnoSerializer(read_only=True)
    idcobertura = CoberturaSerializer(read_only=True)
    
    class Meta(TurnoSerializer.Meta):
        pass

class TurnoCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear turnos"""
    class Meta:
        model = Turno
        fields = [
            'idpaciente', 'idprofesional', 'idcentro', 'idespecialidadpractica',
            'fecha', 'hora', 'observaciones_paciente', 'idcobertura',
            'es_particular', 'cobra_profesional'
        ]
    
    def validate(self, data):
        """Validaciones personalizadas para la creación de turnos"""
        from django.utils import timezone
        from datetime import datetime, timedelta
        
        fecha = data['fecha']
        hora = data['hora']
        profesional = data['idprofesional']
        centro = data['idcentro']
        
        # Validar que la fecha no sea pasada
        if fecha < timezone.now().date():
            raise serializers.ValidationError("No se puede agendar un turno en una fecha pasada")
        
        # Validar disponibilidad del profesional (verificar agenda)
        fecha_hora = datetime.combine(fecha, hora)
        dia_semana = fecha.isoweekday()
        
        # Verificar que exista agenda para ese día y horario
        from MasterModels.modelos_turnos.agendaprofesional import AgendaProfesional
        agenda = AgendaProfesional.objects.filter(
            idprofesional=profesional,
            idcentro=centro,
            dia_semana=dia_semana,
            hora_inicio__lte=hora,
            hora_fin__gt=hora,
            activo=True,
            fecha_inicio_vigencia__lte=fecha,
        ).filter(
            models.Q(fecha_fin_vigencia__isnull=True) | 
            models.Q(fecha_fin_vigencia__gte=fecha)
        ).first()
        
        if not agenda:
            raise serializers.ValidationError("El profesional no tiene agenda disponible en ese horario")
        
        # Verificar que no exista otro turno en el mismo horario
        turno_existente = Turno.objects.filter(
            idprofesional=profesional,
            idcentro=centro,
            fecha=fecha,
            hora=hora
        ).exclude(idestadoturno__codigo='CANCELADO').first()
        
        if turno_existente:
            raise serializers.ValidationError("Ya existe un turno agendado en ese horario")
        
        return data