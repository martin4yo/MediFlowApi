"""
Urls
"""
from django.urls import path, include
from rest_framework import routers

class Router(routers.DefaultRouter):
    """
    Para PascalName
    """
    pass

router = Router()

# URLS GENERALES

from MasterViewSets.viewsets_general import PracticaViewSet, CentroViewSet, PersonaViewSet, EspecialidadViewSet
from MasterViewSets.viewsets_general import EspecialidadPracticaViewSet, CoberturaViewSet, CoberturaPlanViewSet
from MasterViewSets.viewsets_general import PracticaPlanViewSet, DocumentoViewSet, GeneroViewSet, TenantViewSet, UsuarioTenantViewSet

# URLS PROFESIONALES 
from MasterViewSets.viewsets_profesionales import ProfesionalViewSet, ProfesionalEmailViewSet, ProfesionalTelefonoViewSet
from MasterViewSets.viewsets_profesionales import ProfesionalDocumentoViewSet, ProfesionalPracticaViewSet, ProfesionalPracticaCentroViewSet

#URL PACIENTES
from MasterViewSets.viewsets_pacientes import PacienteViewSet, PacienteHistoriaViewSet, PacienteHistoriaAdjuntoViewSet, PacienteTelefonoViewSet
from MasterViewSets.viewsets_pacientes import PacienteEmailViewSet, PacienteHistoriaRecetaViewSet

# URL TURNOS
from MasterViewSets.viewsets_turnos import EstadoTurnoViewSet, AgendaProfesionalViewSet, TurnoViewSet, ExcepcionAgendaViewSet

# URL FINANCIEROS
from MasterViewSets.viewsets_financieros import PagoViewSet, ConfiguracionComisionViewSet, LiquidacionViewSet, GastoAdministrativoViewSet, MovimientoCajaViewSet

# URL NOTIFICACIONES
from MasterViewSets.viewsets_notificaciones import PlantillaNotificacionViewSet, NotificacionViewSet

# URL REPORTES
from MasterViewSets.viewsets_reportes import ReporteViewSet, ReporteEjecutadoViewSet

# URL AUTENTICACION
from MasterViewSets.viewsets_auth import UsuarioViewSet, RolViewSet, PermisoViewSet, SesionViewSet

# ROUTERS 
router.register('api/general/persona', PersonaViewSet, 'personas')
router.register('api/general/practica', PracticaViewSet, 'practicas')
router.register('api/general/centro', CentroViewSet, 'centros')
router.register('api/general/especialidad', EspecialidadViewSet, 'especialidades')
router.register('api/general/especialidadpractica', EspecialidadPracticaViewSet, 'especialidadespracticas')
router.register('api/general/cobertura', CoberturaViewSet, 'coberturas')
router.register('api/general/coberturaplan', CoberturaPlanViewSet, 'coberturasplanes')
router.register('api/general/practicaplan', PracticaPlanViewSet, 'practicasplanes')
router.register('api/general/documento', DocumentoViewSet, 'documentos')
router.register('api/general/genero', GeneroViewSet, 'generos')
router.register('api/general/tenant', TenantViewSet, 'tenants')
router.register('api/general/usuario-tenant', UsuarioTenantViewSet, 'usuarios-tenants')

# ROUTERS PROFESIONALES
router.register('api/profesionales/profesional', ProfesionalViewSet, 'profesionales')
router.register('api/profesionales/profesionalemail', ProfesionalEmailViewSet, 'profesionalemails') 
router.register('api/profesionales/profesionaltelefono', ProfesionalTelefonoViewSet, 'profesionaltelefonos')        
router.register('api/profesionales/profesionaldocumento', ProfesionalDocumentoViewSet, 'profesionaldocumentos')
router.register('api/profesionales/profesionalpractica', ProfesionalPracticaViewSet, 'profesionalpracticas')    
router.register('api/profesionales/profesionalpracticacentro', ProfesionalPracticaCentroViewSet, 'profesionalpracticacentros')  

# ROUTERS PACIENTES
router.register('api/pacientes/paciente', PacienteViewSet, 'pacientes')
router.register('api/pacientes/pacienteemail', PacienteEmailViewSet, 'pacienteemails')
router.register('api/pacientes/pacientetelefono', PacienteTelefonoViewSet, 'pacientetelefonos')
router.register('api/pacientes/pacientehistoria', PacienteHistoriaViewSet, 'pacientehistorias')
router.register('api/pacientes/pacientehistoriaadjunto', PacienteHistoriaAdjuntoViewSet, 'pacientehistoriasadjuntos')
router.register('api/pacientes/pacientehistoriareceta', PacienteHistoriaRecetaViewSet, 'pacientehistoriasrecetas')

# ROUTERS TURNOS
router.register('api/turnos/estadoturno', EstadoTurnoViewSet, 'estadosturnos')
router.register('api/turnos/agendaprofesional', AgendaProfesionalViewSet, 'agendasprofesionales')
router.register('api/turnos/turno', TurnoViewSet, 'turnos')
router.register('api/turnos/excepcionagenda', ExcepcionAgendaViewSet, 'excepcionesagenda')

# ROUTERS FINANCIEROS
router.register('api/financieros/pago', PagoViewSet, 'pagos')
router.register('api/financieros/configuracioncomision', ConfiguracionComisionViewSet, 'configuracionescomision')
router.register('api/financieros/liquidacion', LiquidacionViewSet, 'liquidaciones')
router.register('api/financieros/gastoadministrativo', GastoAdministrativoViewSet, 'gastosadministrativos')
router.register('api/financieros/movimientocaja', MovimientoCajaViewSet, 'movimientoscaja')

# ROUTERS NOTIFICACIONES
router.register('api/notificaciones/plantillanotificacion', PlantillaNotificacionViewSet, 'plantillasnotificacion')
router.register('api/notificaciones/notificacion', NotificacionViewSet, 'notificaciones')

# ROUTERS REPORTES
router.register('api/reportes/reporte', ReporteViewSet, 'reportes')
router.register('api/reportes/reporteejecutado', ReporteEjecutadoViewSet, 'reportesejecutados')

# ROUTERS AUTENTICACION
router.register('api/auth/usuario', UsuarioViewSet, 'usuarios')
router.register('api/auth/rol', RolViewSet, 'roles')
router.register('api/auth/permiso', PermisoViewSet, 'permisos')
router.register('api/auth/sesion', SesionViewSet, 'sesiones')

urlpatterns = [
    path('', include(router.urls)),
    # ... otras URLs ...
]
