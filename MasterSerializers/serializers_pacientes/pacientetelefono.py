from rest_framework import serializers
from MasterModels.modelos_pacientes import PacienteTelefono

class PacienteTelefonoSerializer(serializers.ModelSerializer):
    """ Serializador """
    class Meta:
        """ Clase """
        model = PacienteTelefono
        fields = '__all__'  # O especifica los campos que deseas incluir
        read_only_fields = ('created_at', 'updated_at')


