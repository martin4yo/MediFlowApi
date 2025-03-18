from rest_framework import serializers
from MasterModels.modelos_profesionales import ProfesionalPracticaCentro

class ProfesionalPracticaCentroSerializer(serializers.ModelSerializer):
    """ Serializador """
    class Meta:
        """ Clase """
        model = ProfesionalPracticaCentro
        fields = '__all__'  # O especifica los campos que deseas incluir
        read_only_fields = ('created_at', 'updated_at')


