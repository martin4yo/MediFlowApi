from rest_framework import serializers
from MasterModels.modelos_general.practicaplan import PracticaPlan

class PracticaPlanSerializer(serializers.ModelSerializer):
    """ Serializador """
    class Meta:
        """ Clase """
        model = PracticaPlan
        fields = '__all__'  # O especifica los campos que deseas incluir
        read_only_fields = ('created_at', 'updated_at')


