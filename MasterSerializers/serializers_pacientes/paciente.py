from rest_framework import serializers
from MasterModels.modelos_pacientes import Paciente 


class PacienteSerializer(serializers.ModelSerializer):
    """ Serializador """
    class Meta:
        """ Clase """
        model = Paciente
        fields = '__all__'  # O especifica los campos que deseas incluir
        read_only_fields = ('created_at', 'updated_at')


