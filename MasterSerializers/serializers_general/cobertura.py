from rest_framework import serializers
from MasterModels.modelos_general.cobertura import Cobertura

class CoberturaSerializer(serializers.ModelSerializer):
    """ Serializador """
    class Meta:
        """ Clase """
        model = Cobertura
        fields = '__all__'  # O especifica los campos que deseas incluir
        read_only_fields = ('created_at', 'updated_at')


