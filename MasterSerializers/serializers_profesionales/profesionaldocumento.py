from rest_framework import serializers
from MasterModels.modelos_profesionales import ProfesionalDocumento

class ProfesionalDocumentoSerializer(serializers.ModelSerializer):
    """ Serializador """
    class Meta:
        """ Clase """
        model = ProfesionalDocumento
        fields = '__all__'  # O especifica los campos que deseas incluir
        read_only_fields = ('created_at', 'updated_at')


