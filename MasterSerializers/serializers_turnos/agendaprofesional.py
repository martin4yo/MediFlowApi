from rest_framework import serializers
from MasterModels.modelos_turnos.agendaprofesional import AgendaProfesional
from MasterSerializers.serializers_profesionales.profesional import ProfesionalSerializer
from MasterSerializers.serializers_general.centro import CentroSerializer
from MasterSerializers.serializers_general.especialidadpractica import EspecialidadPracticaSerializer

class AgendaProfesionalSerializer(serializers.ModelSerializer):
    profesional_nombre = serializers.CharField(source='idprofesional.nombre', read_only=True)
    profesional_apellido = serializers.CharField(source='idprofesional.apellido', read_only=True)
    centro_nombre = serializers.CharField(source='idcentro.nombre', read_only=True)
    especialidad_practica_nombre = serializers.CharField(source='idespecialidadpractica.idpractica.nombre', read_only=True)
    
    class Meta:
        model = AgendaProfesional
        fields = [
            'id', 'idprofesional', 'idcentro', 'idespecialidadpractica',
            'dia_semana', 'hora_inicio', 'hora_fin', 'duracion_turno_minutos',
            'dias_adelanto', 'activo', 'fecha_inicio_vigencia', 'fecha_fin_vigencia',
            'profesional_nombre', 'profesional_apellido', 'centro_nombre', 'especialidad_practica_nombre',
            'created_at', 'updated_at', 'disabled'
        ]

class AgendaProfesionalDetailSerializer(AgendaProfesionalSerializer):
    idprofesional = ProfesionalSerializer(read_only=True)
    idcentro = CentroSerializer(read_only=True)
    idespecialidadpractica = EspecialidadPracticaSerializer(read_only=True)
    
    class Meta(AgendaProfesionalSerializer.Meta):
        pass