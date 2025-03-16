from rest_framework import serializers
from MasterModels.modelos_general.especialidad import Especialidad

class EspecialidadSerializer(serializers.ModelSerializer):
    """ Serializador """
    class Meta:
        """ Clase """
        model = Especialidad
        fields = '__all__'  # O especifica los campos que deseas incluir
        read_only_fields = ('created_at', 'updated_at')


