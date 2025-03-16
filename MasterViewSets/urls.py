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

#from MasterViewSets.viewsets_general import PersonaViewSet, PersonaRolViewSet, PaisViewSet, ProvinciaViewSet, CodigoPostalViewSet, TipoCambioViewSet
# from MasterViewSets.viewsets_general import RolViewSet, ModuloViewSet, MascaraViewSet, FormaPagoViewSet, FormaPagoDetalleViewSet, IdiomaViewSet
# from MasterViewSets.viewsets_general import SectorViewSet, IndiceViewSet, PartidoViewSet, TipoIndiceViewSet, MonedaViewSet, TipoDocumentoViewSet
# from MasterViewSets.viewsets_general import TipoFrecuenciaViewSet, TipoValorViewSet, UnidadMedidaViewSet, IncotermsViewSet, TipoResponsableViewSet
# from MasterViewSets.viewsets_general import TablasViewSet, TablasConCodigoViewSet

# router.register('api/general/persona', PersonaViewSet, 'personas')
# router.register('api/general/pais', PaisViewSet, 'paises')
# router.register('api/general/provincia', ProvinciaViewSet, 'provincias')
# router.register('api/general/codigopostal', CodigoPostalViewSet, 'codigospostales')
# router.register('api/general/rol', RolViewSet, 'roles')
# router.register('api/general/modulo', ModuloViewSet, 'modulos')
# router.register('api/general/mascara', MascaraViewSet, 'mascaras')
# router.register('api/general/formapago', FormaPagoViewSet, 'formaspago')
# router.register('api/general/formapagodetalle', FormaPagoDetalleViewSet, 'formaspagodetalle')
# router.register('api/general/tipocambio', TipoCambioViewSet, 'tiposcambio')
# router.register('api/general/personarol', PersonaRolViewSet, 'personasroles')
# router.register('api/general/tipoindice', TipoIndiceViewSet, 'tiposindice')
# router.register('api/general/indice', IndiceViewSet, 'indices')
# router.register('api/general/partido', PartidoViewSet, 'partidos')
# router.register('api/general/sector', SectorViewSet, 'sectores')
# router.register('api/general/idioma', IdiomaViewSet, 'idiomas')
# router.register('api/general/moneda', MonedaViewSet, 'monedas')
# router.register('api/general/tipodocumento', TipoDocumentoViewSet, 'tiposdocumento')
# router.register('api/general/tipofrecuencia', TipoFrecuenciaViewSet, 'tiposfrecuencia')
# router.register('api/general/tipovalor', TipoValorViewSet, 'tiposvalor')
# router.register('api/general/unidadmedida', UnidadMedidaViewSet, 'unidadesmedida')
# router.register('api/general/incoterms', IncotermsViewSet, 'incoterms')
# router.register('api/general/tiporesponsable', TipoResponsableViewSet, 'tiposresponsable')
# router.register('api/general/tablas', TablasViewSet, 'tablas')
# router.register('api/general/tablasconcodigo', TablasConCodigoViewSet, 'tablasconcodigo')

# # URLS DE IMPUESTOS

# from MasterViewSets.viewsets_impuestos import TipoSujetoViewSet, ConceptoIncluidoViewSet
# from MasterViewSets.viewsets_impuestos import TipoComprobanteViewSet
# from MasterViewSets.viewsets_impuestos import AlicuotaImpuestoViewSet, PadronImpuestoViewSet
# from MasterViewSets.viewsets_impuestos import TipoCalculoViewSet,  ClasificacionImpuestoViewSet
# from MasterViewSets.viewsets_impuestos import TipoImpuestoViewSet, CuitPaisViewSet, ImpuestoViewSet

# router.register('api/impuestos/tiposujeto', TipoSujetoViewSet, 'tipossujeto')
# router.register('api/impuestos/conceptoincluido', ConceptoIncluidoViewSet, 'conceptosincluidos')
# router.register('api/impuestos/tipocomprobante', TipoComprobanteViewSet, 'tiposcomprobante')
# router.register('api/impuestos/cuitpais', CuitPaisViewSet, 'cuitpaises')
# router.register('api/impuestos/alicuotaimpuesto', AlicuotaImpuestoViewSet, 'alicuotasimpuestos')
# router.register('api/impuestos/padronimpuesto', PadronImpuestoViewSet, 'padronesimpuesto')
# router.register('api/impuestos/tipocalculo', TipoCalculoViewSet, 'tiposcalculo')
# router.register('api/impuestos/clasificacionimpuesto', ClasificacionImpuestoViewSet, 'clasificacionesimpuestos')
# router.register('api/impuestos/tipoimpuesto', TipoImpuestoViewSet, 'tiposimpuestos')
# router.register('api/impuestos/impuesto', ImpuestoViewSet, 'impuestos')

# # URLS DE CONTABILIDAD

# from MasterViewSets.viewsets_contabilidad import TipoAjusteViewSet, PlanCuentasViewSet

# router.register('api/contabilidad/tipoajuste', TipoAjusteViewSet, 'tiposajuste')
# router.register('api/contabilidad/plancuentas', PlanCuentasViewSet, 'plancuentas')

# # URLS DE ENTIDADES 

# from MasterViewSets.viewsets_entidad import EntidadViewSet, ZonaViewSet, CondicionCrediticiaEntidadViewSet
# from MasterViewSets.viewsets_entidad import ImpuestoEntidadViewSet, EjecutivoEntidadViewSet, ContactoEntidadViewSet
# from MasterViewSets.viewsets_entidad import DireccionEntidadViewSet, ModuloEntidadViewSet, SectorEntidadViewSet
# from MasterViewSets.viewsets_entidad import FormaPagoEntidadViewSet, DatosFiscalesEntidadViewSet, ListaPrecioEntidadViewSet

# from MasterViewSets.viewsets_general import TipoSedeViewSet, TipoDomicilioViewSet

# router.register('api/entidades/entidad', EntidadViewSet, 'entidades')
# router.register('api/entidades/zona', ZonaViewSet, 'zonas')
# router.register('api/entidades/condicioncrediticiaentidad', CondicionCrediticiaEntidadViewSet, 'condicionescrediticiasentidad')
# router.register('api/entidades/impuestoentidad', ImpuestoEntidadViewSet, 'impuestosentidad')
# router.register('api/entidades/ejecutivoentidad', EjecutivoEntidadViewSet, 'ejecutivosentidad')
# router.register('api/entidades/contactoentidad', ContactoEntidadViewSet, 'contactosentidad')
# router.register('api/entidades/tiposede', TipoSedeViewSet, 'tipossede')
# router.register('api/entidades/tipodomicilio', TipoDomicilioViewSet, 'tiposdomicilio')
# router.register('api/entidades/direccionentidad', DireccionEntidadViewSet, 'direccionesentidad')
# router.register('api/entidades/moduloentidad', ModuloEntidadViewSet, 'modulosentidad')
# router.register('api/entidades/sectorentidad', SectorEntidadViewSet, 'sectoresentidad')
# router.register('api/entidades/formapagoentidad', FormaPagoEntidadViewSet, 'formaspagoentidad')
# router.register('api/entidades/datosfiscalesentidad', DatosFiscalesEntidadViewSet, 'datosfiscalesentidad')
# router.register('api/productos/listaprecioentidad', ListaPrecioEntidadViewSet, 'listasprecioentidad')

# # URLS DE PRODUCTOS 

# from MasterViewSets.viewsets_producto import ListaPrecioViewSet, AtributoViewSet, AtributoProductoViewSet, AtributoValorViewSet, AtributoTipoViewSet
# from MasterViewSets.viewsets_producto import ClaseProductoViewSet, ContabilidadProductoViewSet, ConversionProductoViewSet
# from MasterViewSets.viewsets_producto import ProductoViewSet, TipoProductoViewSet, ListaTipoViewSet, PrecioViewSet


# router.register('api/productos/listaprecios', ListaPrecioViewSet, 'listasprecios')
# router.register('api/productos/atributo', AtributoViewSet, 'atributos')
# router.register('api/productos/atributoproducto', AtributoProductoViewSet, 'atributosproducto')
# router.register('api/productos/atributotipo', AtributoTipoViewSet, 'atributostipo')
# router.register('api/productos/atributovalor', AtributoValorViewSet, 'atributosvalor')
# router.register('api/productos/claseproducto', ClaseProductoViewSet, 'clasesproducto')
# router.register('api/productos/contabilidadproducto', ContabilidadProductoViewSet, 'contabilidadproductos')
# router.register('api/productos/conversionproducto', ConversionProductoViewSet, 'conversionesproductos')
# router.register('api/productos/producto', ProductoViewSet, 'productos')
# router.register('api/productos/tipoproducto', TipoProductoViewSet, 'tiposproducto')
# router.register('api/productos/listatipo', ListaTipoViewSet, 'listatipos')
# router.register('api/productos/precio', PrecioViewSet, 'precios')

urlpatterns = [
    path('', include(router.urls)),
    # ... otras URLs ...
]
