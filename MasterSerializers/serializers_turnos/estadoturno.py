from rest_framework import serializers
from MasterModels.modelos_turnos.estadoturno import EstadoTurno

class EstadoTurnoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoTurno
        fields = ['id', 'codigo', 'nombre', 'descripcion', 'color', 'created_at', 'updated_at', 'disabled']