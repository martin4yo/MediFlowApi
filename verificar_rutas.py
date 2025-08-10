#!/usr/bin/env python
"""
Script para verificar todas las rutas del API
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MediFlowConnect.settings')
django.setup()

from django.urls import get_resolver
from rest_framework import routers
from MasterViewSets.urls import router

def mostrar_rutas_api():
    """Muestra todas las rutas registradas en el API"""
    print("=" * 80)
    print("RUTAS DEL API MEDIFLOW")
    print("=" * 80)
    
    print(f"\nTOTAL DE RUTAS REGISTRADAS: {len(router.registry)}")
    
    # Agrupar por módulo
    modulos = {}
    for prefix, viewset, basename in router.registry:
        modulo = prefix.split('/')[1]  # api/modulo/endpoint
        if modulo not in modulos:
            modulos[modulo] = []
        modulos[modulo].append({
            'prefix': prefix,
            'viewset': viewset.__name__,
            'basename': basename
        })
    
    # Mostrar por módulo
    for modulo, rutas in modulos.items():
        print(f"\n[MODULO] {modulo.upper()}")
        print("-" * 50)
        
        for ruta in rutas:
            print(f"  * /{ruta['prefix']}/")
            print(f"    ViewSet: {ruta['viewset']}")
            print(f"    Basename: {ruta['basename']}")
            print()
    
    print("\n" + "=" * 80)
    print("ENDPOINTS POR MÓDULO")
    print("=" * 80)
    
    # Contar endpoints por módulo
    for modulo, rutas in modulos.items():
        count = len(rutas)
        print(f"{modulo.upper():20} - {count:2d} endpoints")
    
    print("\n" + "=" * 80)
    print("EJEMPLOS DE USO")
    print("=" * 80)
    
    ejemplos = [
        ("Listar turnos", "GET /api/turnos/turno/"),
        ("Crear turno", "POST /api/turnos/turno/"),
        ("Listar pagos", "GET /api/financieros/pago/"),
        ("Estadísticas pagos", "GET /api/financieros/pago/estadisticas/"),
        ("Ejecutar reporte", "POST /api/reportes/reporte/{id}/ejecutar/"),
        ("Notificaciones pendientes", "GET /api/notificaciones/notificacion/pendientes/"),
        ("Crear plantilla notif.", "POST /api/notificaciones/plantillanotificacion/"),
        ("Dashboard reportes", "GET /api/reportes/reporte/dashboard/")
    ]
    
    for descripcion, endpoint in ejemplos:
        print(f"  {descripcion:25} - {endpoint}")

if __name__ == '__main__':
    try:
        mostrar_rutas_api()
        print("\n[OK] Sistema de rutas funcionando correctamente!")
        print("URL Para ver la API en accion: http://localhost:8000/api/")
        print("URL Panel de administracion: http://localhost:8000/admin/")
        
    except Exception as e:
        print(f"[ERROR] Error al verificar rutas: {str(e)}")
        sys.exit(1)