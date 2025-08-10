from rest_framework import serializers
from MasterModels.modelos_turnos.excepcionagenda import ExcepcionAgenda
from MasterSerializers.serializers_profesionales.profesional import ProfesionalSerializer
from MasterSerializers.serializers_general.centro import CentroSerializer

class ExcepcionAgendaSerializer(serializers.ModelSerializer):
    profesional_nombre_completo = serializers.CharField(source='idprofesional.nombre_completo', read_only=True)
    centro_nombre = serializers.CharField(source='idcentro.nombre', read_only=True)
    
    class Meta:
        model = ExcepcionAgenda
        fields = [
            'id', 'idprofesional', 'idcentro', 'tipo', 'fecha_inicio', 'fecha_fin',
            'hora_inicio', 'hora_fin', 'descripcion', 'observaciones', 
            'afecta_centro_completo', 'profesional_nombre_completo', 'centro_nombre',
            'created_at', 'updated_at', 'disabled'
        ]

class ExcepcionAgendaDetailSerializer(ExcepcionAgendaSerializer):
    idprofesional = ProfesionalSerializer(read_only=True)
    idcentro = CentroSerializer(read_only=True)
    
    class Meta(ExcepcionAgendaSerializer.Meta):
        pass