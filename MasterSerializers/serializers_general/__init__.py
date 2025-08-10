#Importa todos los modulos 
from .centro import CentroSerializer
from .especialidad import EspecialidadSerializer
from .practica import PracticaSerializer
from .persona import PersonaSerializer
from .especialidadpractica import EspecialidadPracticaSerializer
from .cobertura import CoberturaSerializer
from .coberturaplan import CoberturaPlanSerializer
from .practicaplan import PracticaPlanSerializer
from .documento import DocumentoSerializer
from .genero import GeneroSerializer
from .tenant import (
    TenantSerializer, TenantListSerializer, TenantCreateSerializer,
    UsuarioTenantSerializer, AsignarUsuarioTenantSerializer,
    TenantEstadisticasSerializer, CentroTenantSerializer
)
