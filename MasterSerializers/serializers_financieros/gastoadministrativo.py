from rest_framework import serializers
from MasterModels.modelos_financieros.gastoadministrativo import GastoAdministrativo
from MasterSerializers.serializers_general.centro import CentroSerializer

class GastoAdministrativoSerializer(serializers.ModelSerializer):
    centro_nombre = serializers.CharField(source='idcentro.nombre', read_only=True)
    esta_vencido = serializers.BooleanField(read_only=True)
    dias_vencimiento = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = GastoAdministrativo
        fields = [
            'id', 'idcentro', 'categoria', 'subcategoria', 'concepto', 'proveedor',
            'monto', 'iva', 'total', 'fecha_gasto', 'fecha_vencimiento',
            'estado_pago', 'fecha_pago', 'metodo_pago', 'numero_factura',
            'numero_recibo', 'archivo_adjunto', 'es_recurrente', 'observaciones',
            'centro_nombre', 'esta_vencido', 'dias_vencimiento',
            'created_at', 'updated_at', 'disabled'
        ]
        read_only_fields = ['total']

class GastoAdministrativoDetailSerializer(GastoAdministrativoSerializer):
    idcentro = CentroSerializer(read_only=True)
    
    class Meta(GastoAdministrativoSerializer.Meta):
        pass