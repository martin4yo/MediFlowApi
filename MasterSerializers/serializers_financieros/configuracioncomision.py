from rest_framework import serializers
from MasterModels.modelos_financieros.configuracioncomision import ConfiguracionComision
from MasterSerializers.serializers_profesionales.profesional import ProfesionalSerializer
from MasterSerializers.serializers_general.centro import CentroSerializer
from MasterSerializers.serializers_general.especialidadpractica import EspecialidadPracticaSerializer

class ConfiguracionComisionSerializer(serializers.ModelSerializer):
    profesional_nombre = serializers.CharField(source='idprofesional.nombre_completo', read_only=True)
    centro_nombre = serializers.CharField(source='idcentro.nombre', read_only=True)
    practica_nombre = serializers.CharField(source='idespecialidadpractica.idpractica.nombre', read_only=True)
    especialidad_nombre = serializers.CharField(source='idespecialidadpractica.idespecialidad.nombre', read_only=True)
    
    class Meta:
        model = ConfiguracionComision
        fields = [
            'id', 'idprofesional', 'idcentro', 'idespecialidadpractica',
            'porcentaje_profesional', 'porcentaje_centro', 'prioridad',
            'fecha_inicio', 'fecha_fin', 'activo', 'descripcion', 'observaciones',
            'profesional_nombre', 'centro_nombre', 'practica_nombre', 'especialidad_nombre',
            'created_at', 'updated_at', 'disabled'
        ]

class ConfiguracionComisionDetailSerializer(ConfiguracionComisionSerializer):
    idprofesional = ProfesionalSerializer(read_only=True)
    idcentro = CentroSerializer(read_only=True)
    idespecialidadpractica = EspecialidadPracticaSerializer(read_only=True)
    
    class Meta(ConfiguracionComisionSerializer.Meta):
        pass