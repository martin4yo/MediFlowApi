from rest_framework import serializers
from MasterModels.modelos_financieros.movimientocaja import MovimientoCaja
from MasterSerializers.serializers_general.centro import CentroSerializer
from MasterSerializers.serializers_general.persona import PersonaSerializer

class MovimientoCajaSerializer(serializers.ModelSerializer):
    centro_nombre = serializers.CharField(source='idcentro.nombre', read_only=True)
    usuario_nombre = serializers.CharField(source='usuario_responsable.nombre_completo', read_only=True)
    
    class Meta:
        model = MovimientoCaja
        fields = [
            'id', 'idcentro', 'tipo_movimiento', 'categoria', 'concepto', 'monto',
            'idpago', 'idliquidacion', 'idgastoadministrativo', 'fecha_movimiento',
            'metodo', 'saldo_anterior', 'saldo_posterior', 'usuario_responsable',
            'comprobante', 'observaciones', 'centro_nombre', 'usuario_nombre',
            'created_at', 'updated_at', 'disabled'
        ]
        read_only_fields = ['saldo_posterior']

class MovimientoCajaDetailSerializer(MovimientoCajaSerializer):
    idcentro = CentroSerializer(read_only=True)
    usuario_responsable = PersonaSerializer(read_only=True)
    
    class Meta(MovimientoCajaSerializer.Meta):
        pass