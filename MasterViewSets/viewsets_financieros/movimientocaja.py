from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from django.db.models import Sum, Count, Q
from django.db import models
from datetime import datetime, timedelta

from MasterModels.modelos_financieros.movimientocaja import MovimientoCaja
from MasterSerializers.serializers_financieros.movimientocaja import MovimientoCajaSerializer, MovimientoCajaDetailSerializer

class MovimientoCajaViewSet(viewsets.ModelViewSet):
    queryset = MovimientoCaja.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = [
        'idcentro', 'tipo_movimiento', 'categoria', 'metodo', 
        'fecha_movimiento', 'usuario_responsable', 'disabled'
    ]
    ordering_fields = ['id', 'fecha_movimiento', 'monto', 'created_at']
    ordering = ['-fecha_movimiento']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return MovimientoCajaDetailSerializer
        return MovimientoCajaSerializer

    def perform_create(self, serializer):
        """Al crear un movimiento, calcular el saldo automáticamente"""
        centro = serializer.validated_data['idcentro']
        
        # Obtener el saldo anterior
        saldo_anterior = MovimientoCaja.calcular_saldo_actual(centro.id)
        
        serializer.save(
            saldo_anterior=saldo_anterior,
            usuario_responsable=self.request.user.persona if hasattr(self.request.user, 'persona') else None
        )

    @action(detail=False, methods=['get'])
    def saldo_actual(self, request):
        """Obtiene el saldo actual de caja para un centro"""
        centro_id = request.query_params.get('centro_id')
        fecha_hasta = request.query_params.get('fecha_hasta')
        
        if not centro_id:
            return Response(
                {"error": "Falta parámetro: centro_id"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        fecha_hasta_obj = None
        if fecha_hasta:
            try:
                fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d')
            except ValueError:
                return Response(
                    {"error": "Formato de fecha inválido. Usar YYYY-MM-DD"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        saldo = MovimientoCaja.calcular_saldo_actual(centro_id, fecha_hasta_obj)
        
        return Response({
            "centro_id": centro_id,
            "fecha_consulta": fecha_hasta or "actual",
            "saldo": saldo
        })

    @action(detail=False, methods=['get'])
    def flujo_diario(self, request):
        """Flujo de caja diario"""
        centro_id = request.query_params.get('centro_id')
        fecha = request.query_params.get('fecha', datetime.now().date().strftime('%Y-%m-%d'))
        
        if not centro_id:
            return Response(
                {"error": "Falta parámetro: centro_id"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {"error": "Formato de fecha inválido. Usar YYYY-MM-DD"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Movimientos del día
        movimientos_dia = self.get_queryset().filter(
            idcentro_id=centro_id,
            fecha_movimiento__date=fecha
        )
        
        # Resumen de ingresos
        ingresos = movimientos_dia.filter(tipo_movimiento='INGRESO').aggregate(
            total=Sum('monto'),
            cantidad=Count('id')
        )
        
        # Resumen de egresos
        egresos = movimientos_dia.filter(tipo_movimiento='EGRESO').aggregate(
            total=Sum('monto'),
            cantidad=Count('id')
        )
        
        # Saldo inicial (al inicio del día)
        fecha_inicio_dia = datetime.combine(fecha, datetime.min.time())
        saldo_inicial = MovimientoCaja.calcular_saldo_actual(centro_id, fecha_inicio_dia)
        
        # Saldo final
        saldo_final = saldo_inicial + (ingresos['total'] or 0) - (egresos['total'] or 0)
        
        # Movimientos detallados
        serializer = self.get_serializer(movimientos_dia, many=True)
        
        return Response({
            "fecha": fecha,
            "centro_id": centro_id,
            "saldo_inicial": saldo_inicial,
            "saldo_final": saldo_final,
            "ingresos": {
                "total": ingresos['total'] or 0,
                "cantidad": ingresos['cantidad']
            },
            "egresos": {
                "total": egresos['total'] or 0,
                "cantidad": egresos['cantidad']
            },
            "movimientos": serializer.data
        })

    @action(detail=False, methods=['get'])
    def reporte_mensual(self, request):
        """Reporte mensual de movimientos"""
        centro_id = request.query_params.get('centro_id')
        ano = request.query_params.get('ano', datetime.now().year)
        mes = request.query_params.get('mes', datetime.now().month)
        
        if not centro_id:
            return Response(
                {"error": "Falta parámetro: centro_id"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            ano = int(ano)
            mes = int(mes)
        except ValueError:
            return Response(
                {"error": "Año y mes deben ser números enteros"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Movimientos del mes
        movimientos_mes = self.get_queryset().filter(
            idcentro_id=centro_id,
            fecha_movimiento__year=ano,
            fecha_movimiento__month=mes
        )
        
        # Resumen por tipo de movimiento
        por_tipo = movimientos_mes.values('tipo_movimiento').annotate(
            total=Sum('monto'),
            cantidad=Count('id')
        ).order_by('tipo_movimiento')
        
        # Resumen por categoría
        por_categoria = movimientos_mes.values('categoria').annotate(
            total=Sum('monto'),
            cantidad=Count('id')
        ).order_by('-total')
        
        # Resumen por método
        por_metodo = movimientos_mes.values('metodo').annotate(
            total=Sum('monto'),
            cantidad=Count('id')
        ).order_by('-total')
        
        # Totales generales
        totales = movimientos_mes.aggregate(
            total_ingresos=Sum('monto', filter=models.Q(tipo_movimiento='INGRESO')),
            total_egresos=Sum('monto', filter=models.Q(tipo_movimiento='EGRESO')),
            cantidad_total=Count('id')
        )
        
        # Calcular resultado neto
        resultado_neto = (totales['total_ingresos'] or 0) - (totales['total_egresos'] or 0)
        
        return Response({
            "periodo": f"{mes:02d}/{ano}",
            "centro_id": centro_id,
            "resumen_por_tipo": por_tipo,
            "resumen_por_categoria": por_categoria,
            "resumen_por_metodo": por_metodo,
            "totales": {
                **totales,
                "resultado_neto": resultado_neto
            }
        })

    @action(detail=False, methods=['get'])
    def balance_general(self, request):
        """Balance general hasta una fecha específica"""
        centro_id = request.query_params.get('centro_id')
        fecha_hasta = request.query_params.get('fecha_hasta')
        
        if not centro_id:
            return Response(
                {"error": "Falta parámetro: centro_id"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        fecha_hasta_obj = None
        if fecha_hasta:
            try:
                fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d')
            except ValueError:
                return Response(
                    {"error": "Formato de fecha inválido. Usar YYYY-MM-DD"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Filtro base
        queryset = self.get_queryset().filter(idcentro_id=centro_id)
        if fecha_hasta_obj:
            queryset = queryset.filter(fecha_movimiento__lte=fecha_hasta_obj)
        
        # Totales por tipo
        ingresos_totales = queryset.filter(tipo_movimiento='INGRESO').aggregate(Sum('monto'))['monto__sum'] or 0
        egresos_totales = queryset.filter(tipo_movimiento='EGRESO').aggregate(Sum('monto'))['monto__sum'] or 0
        
        # Desglose de ingresos por categoría
        ingresos_detalle = queryset.filter(tipo_movimiento='INGRESO').values('categoria').annotate(
            total=Sum('monto'),
            cantidad=Count('id')
        ).order_by('-total')
        
        # Desglose de egresos por categoría
        egresos_detalle = queryset.filter(tipo_movimiento='EGRESO').values('categoria').annotate(
            total=Sum('monto'),
            cantidad=Count('id')
        ).order_by('-total')
        
        # Saldo final
        saldo_final = ingresos_totales - egresos_totales
        
        return Response({
            "centro_id": centro_id,
            "fecha_corte": fecha_hasta or "actual",
            "resumen": {
                "total_ingresos": ingresos_totales,
                "total_egresos": egresos_totales,
                "saldo_final": saldo_final
            },
            "detalle_ingresos": ingresos_detalle,
            "detalle_egresos": egresos_detalle
        })