"""
Script para crear datos iniciales del sistema de turnos
Ejecutar después de aplicar las migraciones
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MediFlowConnect.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from MasterModels.modelos_turnos.estadoturno import EstadoTurno

def crear_estados_turno():
    """Crear estados de turno predefinidos"""
    estados = [
        {
            'codigo': 'SOLICITADO',
            'nombre': 'Solicitado',
            'descripcion': 'Turno solicitado pendiente de confirmación',
            'color': '#FCD34D'  # Amarillo
        },
        {
            'codigo': 'CONFIRMADO',
            'nombre': 'Confirmado',
            'descripcion': 'Turno confirmado por recepción',
            'color': '#10B981'  # Verde
        },
        {
            'codigo': 'EN_ESPERA',
            'nombre': 'En Espera',
            'descripcion': 'Paciente presente, aguardando atención',
            'color': '#3B82F6'  # Azul
        },
        {
            'codigo': 'EN_ATENCION',
            'nombre': 'En Atención',
            'descripcion': 'Paciente siendo atendido por el profesional',
            'color': '#8B5CF6'  # Púrpura
        },
        {
            'codigo': 'ATENDIDO',
            'nombre': 'Atendido',
            'descripcion': 'Atención finalizada correctamente',
            'color': '#059669'  # Verde oscuro
        },
        {
            'codigo': 'CANCELADO',
            'nombre': 'Cancelado',
            'descripcion': 'Turno cancelado por paciente o centro',
            'color': '#DC2626'  # Rojo
        },
        {
            'codigo': 'NO_ASISTIO',
            'nombre': 'No Asistió',
            'descripcion': 'Paciente no se presentó al turno',
            'color': '#9CA3AF'  # Gris
        }
    ]
    
    print("Creando estados de turno...")
    for estado_data in estados:
        estado, created = EstadoTurno.objects.get_or_create(
            codigo=estado_data['codigo'],
            defaults=estado_data
        )
        if created:
            print(f"[OK] Creado: {estado.codigo} - {estado.nombre}")
        else:
            print(f"[--] Ya existe: {estado.codigo} - {estado.nombre}")

if __name__ == '__main__':
    print("=== CREANDO DATOS INICIALES ===")
    try:
        crear_estados_turno()
        print("=== DATOS INICIALES CREADOS EXITOSAMENTE ===")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)