from rest_framework import serializers
from MasterModels.modelos_pacientes.pacientehistoriareceta import PacienteHistoriaReceta

class PacienteHistoriaRecetaSerializer(serializers.ModelSerializer):
    # Propiedades calculadas
    esta_vencido = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = PacienteHistoriaReceta
        fields = [
            'id', 'idpacientehistoria', 'tipo_receta', 'item', 'dosis', 
            'frecuencia', 'duracion', 'indicaciones', 'observaciones', 
            'urgente', 'fecha_vencimiento', 'completado', 'fecha_completado',
            'esta_vencido', 'created_at', 'updated_at', 'disabled'
        ]


