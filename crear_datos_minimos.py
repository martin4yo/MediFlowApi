"""
Script para crear datos mínimos compatibles con la estructura actual
"""
import os
import sys
import django
from decimal import Decimal
from datetime import date, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MediFlowConnect.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from MasterModels.modelos_general.centro import Centro
from MasterModels.modelos_general.especialidad import Especialidad
from MasterModels.modelos_general.practica import Practica
from MasterModels.modelos_general.especialidadpractica import EspecialidadPractica
from MasterModels.modelos_financieros.configuracioncomision import ConfiguracionComision

def crear_datos_minimos():
    """Crear solo los datos mínimos necesarios para probar el sistema financiero"""
    print("=== CREANDO DATOS MÍNIMOS ===")
    
    # 1. Crear un centro
    centro, created = Centro.objects.get_or_create(
        codigo='DEMO01',
        defaults={
            'nombre': 'Centro Demo',
            'direccion': 'Av. Demo 123',
            'localidad': 'CABA',
            'telefono': '011-1234-5678',
            'mail': 'demo@mediflow.com'
        }
    )
    if created:
        print(f"[OK] Centro: {centro.nombre}")
    
    # 2. Crear especialidades
    especialidades = [
        {'codigo': 'CLIN', 'nombre': 'Clínica Médica'},
        {'codigo': 'CARD', 'nombre': 'Cardiología'}
    ]
    
    for esp_data in especialidades:
        especialidad, created = Especialidad.objects.get_or_create(
            codigo=esp_data['codigo'],
            defaults=esp_data
        )
        if created:
            print(f"[OK] Especialidad: {especialidad.nombre}")
    
    # 3. Crear prácticas con precios
    practicas = [
        {'codigo': 'CONS', 'nombre': 'Consulta', 'precio': 8000, 'duracion': 30},
        {'codigo': 'CTRL', 'nombre': 'Control', 'precio': 6000, 'duracion': 20},
        {'codigo': 'ECG', 'nombre': 'Electrocardiograma', 'precio': 4500, 'duracion': 15}
    ]
    
    for prac_data in practicas:
        practica, created = Practica.objects.get_or_create(
            codigo=prac_data['codigo'],
            defaults={
                'nombre': prac_data['nombre'],
                'precio_base': Decimal(str(prac_data['precio'])),
                'duracion_estimada_minutos': prac_data['duracion']
            }
        )
        if created:
            print(f"[OK] Práctica: {practica.nombre} - ${practica.precio_base}")
    
    # 4. Crear relaciones especialidad-práctica
    relaciones = [
        ('CLIN', 'CONS'),
        ('CLIN', 'CTRL'), 
        ('CARD', 'CONS'),
        ('CARD', 'ECG')
    ]
    
    for esp_cod, prac_cod in relaciones:
        try:
            especialidad = Especialidad.objects.get(codigo=esp_cod)
            practica = Practica.objects.get(codigo=prac_cod)
            
            esp_prac, created = EspecialidadPractica.objects.get_or_create(
                idespecialidad=especialidad,
                idpractica=practica
            )
            if created:
                print(f"[OK] Relación: {especialidad.nombre} - {practica.nombre}")
        except Exception as e:
            print(f"[ERROR] {e}")
    
    # 5. Crear configuración de comisión por defecto
    config, created = ConfiguracionComision.objects.get_or_create(
        idprofesional=None,
        idcentro=None,
        idespecialidadpractica=None,
        defaults={
            'porcentaje_profesional': Decimal('70.00'),
            'porcentaje_centro': Decimal('30.00'),
            'prioridad': 5,
            'fecha_inicio': date(2024, 1, 1),
            'activo': True,
            'descripcion': 'Configuración por defecto: 70% profesional, 30% centro'
        }
    )
    if created:
        print(f"[OK] Configuración comisión: 70%/30%")

def mostrar_instrucciones():
    """Mostrar instrucciones para usar el sistema"""
    print("\n=== SISTEMA LISTO PARA PRUEBAS ===")
    print("\n=== ENDPOINTS PRINCIPALES DISPONIBLES ===")
    
    print("\nGESTION DE TURNOS:")
    print("  GET  /api/turnos/turno/ - Listar turnos")
    print("  POST /api/turnos/turno/ - Crear turno")
    print("  GET  /api/turnos/estadoturno/ - Estados de turno")
    
    print("\nSISTEMA FINANCIERO:")
    print("  GET  /api/financieros/pago/ - Listar pagos")
    print("  POST /api/financieros/pago/ - Procesar pago")
    print("  GET  /api/financieros/pago/resumen_diario/ - Resumen diario")
    print("  GET  /api/financieros/liquidacion/ - Liquidaciones")
    print("  POST /api/financieros/liquidacion/ - Crear liquidacion")
    print("  GET  /api/financieros/movimientocaja/balance_general/ - Balance")
    
    print("\nDATOS CREADOS:")
    print(f"  - {Centro.objects.count()} centro(s)")
    print(f"  - {Especialidad.objects.count()} especialidad(es)")
    print(f"  - {Practica.objects.count()} practica(s)")
    print(f"  - {EspecialidadPractica.objects.count()} relacion(es)")
    print(f"  - {ConfiguracionComision.objects.count()} configuracion(es) de comision")
    
    print("\nPROXIMOS PASOS:")
    print("1. Crear profesionales y pacientes manualmente via Django Admin")
    print("2. Probar crear turnos via API")
    print("3. Procesar pagos (senas y restos)")
    print("4. Generar reportes financieros")
    
    print(f"\nDjango Admin: http://localhost:8000/admin/")
    print(f"API Root: http://localhost:8000/api/")

if __name__ == '__main__':
    try:
        crear_datos_minimos()
        mostrar_instrucciones()
        print("\n[OK] DATOS MINIMOS CREADOS EXITOSAMENTE")
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)