from rest_framework import serializers
from MasterModels.modelos_general.especialidadpractica import EspecialidadPractica

class EspecialidadPracticaSerializer(serializers.ModelSerializer):
    """ Serializador """
    class Meta:
        """ Clase """
        model = EspecialidadPractica
        fields = '__all__'  # O especifica los campos que deseas incluir
        read_only_fields = ('created_at', 'updated_at')


