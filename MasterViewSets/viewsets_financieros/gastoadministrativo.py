from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from django.db.models import Sum, Count, Q
from django.db import models
from datetime import datetime, timedelta

from MasterModels.modelos_financieros.gastoadministrativo import GastoAdministrativo
from MasterSerializers.serializers_financieros.gastoadministrativo import GastoAdministrativoSerializer, GastoAdministrativoDetailSerializer

class GastoAdministrativoViewSet(viewsets.ModelViewSet):
    queryset = GastoAdministrativo.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = [
        'idcentro', 'categoria', 'subcategoria', 'proveedor', 
        'estado_pago', 'fecha_gasto', 'es_recurrente', 'disabled'
    ]
    ordering_fields = ['id', 'fecha_gasto', 'fecha_vencimiento', 'total', 'created_at']
    ordering = ['-fecha_gasto']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return GastoAdministrativoDetailSerializer
        return GastoAdministrativoSerializer

    @action(detail=True, methods=['post'])
    def marcar_pagado(self, request, pk=None):
        """Marca un gasto como pagado"""
        gasto = self.get_object()
        
        if gasto.estado_pago == 'PAGADO':
            return Response(
                {"error": "El gasto ya está marcado como pagado"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        fecha_pago = request.data.get('fecha_pago')
        metodo_pago = request.data.get('metodo_pago')
        
        if fecha_pago:
            try:
                fecha_pago = datetime.strptime(fecha_pago, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {"error": "Formato de fecha inválido. Usar YYYY-MM-DD"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        gasto.marcar_pagado(fecha_pago, metodo_pago)
        
        # Crear movimiento de caja
        from MasterModels.modelos_financieros.movimientocaja import MovimientoCaja
        MovimientoCaja.objects.create(
            idcentro=gasto.idcentro,
            tipo_movimiento='EGRESO',
            categoria='GASTO_ADMIN',
            concepto=f'Gasto administrativo: {gasto.concepto}',
            monto=gasto.total,
            idgastoadministrativo=gasto,
            fecha_movimiento=gasto.fecha_pago,
            metodo=gasto.metodo_pago or 'EFECTIVO'
        )
        
        serializer = self.get_serializer(gasto)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def anular(self, request, pk=None):
        """Anula un gasto"""
        gasto = self.get_object()
        motivo = request.data.get('motivo', '')
        
        gasto.estado_pago = 'ANULADO'
        gasto.observaciones = f'Anulado: {motivo}'
        gasto.save()
        
        serializer = self.get_serializer(gasto)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def vencidos(self, request):
        """Gastos vencidos"""
        centro_id = request.query_params.get('centro_id')
        
        queryset = self.get_queryset().filter(
            estado_pago='PENDIENTE',
            fecha_vencimiento__lt=datetime.now().date()
        )
        
        if centro_id:
            queryset = queryset.filter(idcentro_id=centro_id)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def por_vencer(self, request):
        """Gastos próximos a vencer"""
        centro_id = request.query_params.get('centro_id')
        dias = int(request.query_params.get('dias', 7))  # Por defecto 7 días
        
        fecha_limite = datetime.now().date() + timedelta(days=dias)
        
        queryset = self.get_queryset().filter(
            estado_pago='PENDIENTE',
            fecha_vencimiento__lte=fecha_limite,
            fecha_vencimiento__gte=datetime.now().date()
        )
        
        if centro_id:
            queryset = queryset.filter(idcentro_id=centro_id)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def resumen_mensual(self, request):
        """Resumen de gastos por mes"""
        centro_id = request.query_params.get('centro_id')
        ano = request.query_params.get('ano', datetime.now().year)
        mes = request.query_params.get('mes', datetime.now().month)
        
        try:
            ano = int(ano)
            mes = int(mes)
        except ValueError:
            return Response(
                {"error": "Año y mes deben ser números enteros"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(
            fecha_gasto__year=ano,
            fecha_gasto__month=mes
        )
        
        if centro_id:
            queryset = queryset.filter(idcentro_id=centro_id)
        
        # Resumen por categoría
        por_categoria = queryset.values('categoria').annotate(
            total=Sum('total'),
            cantidad=Count('id')
        ).order_by('-total')
        
        # Resumen por estado
        por_estado = queryset.values('estado_pago').annotate(
            total=Sum('total'),
            cantidad=Count('id')
        ).order_by('-total')
        
        # Totales generales
        totales = queryset.aggregate(
            total_gastos=Sum('total'),
            total_registros=Count('id'),
            total_pagados=Sum('total', filter=models.Q(estado_pago='PAGADO')),
            total_pendientes=Sum('total', filter=models.Q(estado_pago='PENDIENTE'))
        )
        
        return Response({
            'periodo': f"{mes:02d}/{ano}",
            'resumen_por_categoria': por_categoria,
            'resumen_por_estado': por_estado,
            'totales': totales
        })

    @action(detail=False, methods=['get'])
    def recurrentes(self, request):
        """Gastos marcados como recurrentes"""
        centro_id = request.query_params.get('centro_id')
        
        queryset = self.get_queryset().filter(es_recurrente=True)
        
        if centro_id:
            queryset = queryset.filter(idcentro_id=centro_id)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def por_proveedor(self, request):
        """Gastos agrupados por proveedor"""
        centro_id = request.query_params.get('centro_id')
        fecha_desde = request.query_params.get('fecha_desde')
        fecha_hasta = request.query_params.get('fecha_hasta')
        
        queryset = self.get_queryset()
        
        if centro_id:
            queryset = queryset.filter(idcentro_id=centro_id)
        
        if fecha_desde:
            try:
                fecha_desde = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
                queryset = queryset.filter(fecha_gasto__gte=fecha_desde)
            except ValueError:
                pass
        
        if fecha_hasta:
            try:
                fecha_hasta = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
                queryset = queryset.filter(fecha_gasto__lte=fecha_hasta)
            except ValueError:
                pass
        
        # Agrupar por proveedor
        por_proveedor = queryset.values('proveedor').annotate(
            total_gastado=Sum('total'),
            cantidad_gastos=Count('id'),
            total_pendiente=Sum('total', filter=models.Q(estado_pago='PENDIENTE'))
        ).order_by('-total_gastado')
        
        return Response(por_proveedor)