from rest_framework import serializers
from MasterModels.modelos_pacientes.pacientehistoria import PacienteHistoria
from MasterSerializers.serializers_pacientes.paciente import PacienteSerializer
from MasterSerializers.serializers_profesionales.profesional import ProfesionalSerializer
from MasterSerializers.serializers_general.centro import CentroSerializer
from MasterSerializers.serializers_general.especialidadpractica import EspecialidadPracticaSerializer

class PacienteHistoriaSerializer(serializers.ModelSerializer):
    # Campos relacionados
    paciente_nombre = serializers.CharField(source='idpaciente.idpersona.nombre', read_only=True)
    profesional_nombre = serializers.CharField(source='idprofesional.idpersona.nombre', read_only=True)
    centro_nombre = serializers.CharField(source='idcentro.nombre', read_only=True)
    practica_nombre = serializers.CharField(source='idespecialidadpractica.idpractica.nombre', read_only=True)
    especialidad_nombre = serializers.CharField(source='idespecialidadpractica.idespecialidad.nombre', read_only=True)
    
    # Propiedades calculadas
    imc = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    duracion_consulta = serializers.IntegerField(read_only=True)
    presion_arterial = serializers.CharField(read_only=True)
    tiene_recetas = serializers.BooleanField(read_only=True)
    tiene_adjuntos = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = PacienteHistoria
        fields = [
            'id', 'idpaciente', 'idprofesional', 'idturno', 'idespecialidadpractica', 'idcentro',
            'fecha', 'hora_inicio', 'hora_fin', 'motivo_consulta', 'antecedentes', 
            'examen_fisico', 'diagnostico_principal', 'diagnosticos_secundarios',
            'tratamiento', 'indicaciones', 'observaciones', 'proximo_control', 
            'urgente', 'derivacion', 'peso', 'altura', 'presion_sistolica', 
            'presion_diastolica', 'frecuencia_cardiaca', 'temperatura',
            'paciente_nombre', 'profesional_nombre', 'centro_nombre', 
            'practica_nombre', 'especialidad_nombre', 'imc', 'duracion_consulta', 
            'presion_arterial', 'tiene_recetas', 'tiene_adjuntos',
            'created_at', 'updated_at', 'disabled'
        ]

class PacienteHistoriaDetailSerializer(PacienteHistoriaSerializer):
    idpaciente = PacienteSerializer(read_only=True)
    idprofesional = ProfesionalSerializer(read_only=True)
    idcentro = CentroSerializer(read_only=True)
    idespecialidadpractica = EspecialidadPracticaSerializer(read_only=True)
    
    # Incluir recetas y adjuntos
    recetas = serializers.SerializerMethodField()
    adjuntos = serializers.SerializerMethodField()
    
    class Meta(PacienteHistoriaSerializer.Meta):
        fields = PacienteHistoriaSerializer.Meta.fields + ['recetas', 'adjuntos']
    
    def get_recetas(self, obj):
        from MasterSerializers.serializers_pacientes.pacientehistoriareceta import PacienteHistoriaRecetaSerializer
        recetas = obj.pacientehistoriareceta_set.all()
        return PacienteHistoriaRecetaSerializer(recetas, many=True).data
    
    def get_adjuntos(self, obj):
        from MasterSerializers.serializers_pacientes.pacientehistoriaadjunto import PacienteHistoriaAdjuntoSerializer
        adjuntos = obj.pacientehistoriaadjunto_set.all()
        return PacienteHistoriaAdjuntoSerializer(adjuntos, many=True).data


