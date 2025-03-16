from django_filters import rest_framework as filters

from MasterModels.modelos_general.persona import Persona

# class PersonaFilter(filters.FilterSet):

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
        
#         # Recorre todos los campos del modelo y asigna el tipo de filtro en función de su tipo de dato
#         for field in self.Meta.model._meta.get_fields():
#             # Evitar campos que no son de base de datos (relaciones inversas, etc.)
#             if not hasattr(field, 'get_internal_type'):
#                 continue
            
#             field_type = field.get_internal_type()
            
#             if field_type in ['CharField', 'TextField']:
#                 # Para campos de texto, agregar filtro exacto y búsqueda parcial
#                 self.filters[field.name] = filters.CharFilter(field_name=field.name, lookup_expr='icontains')
            
#             elif field_type in ['IntegerField', 'FloatField', 'DecimalField']:
#                 # Para campos numéricos, agregar filtros de rangos
#                 self.filters[field.name] = filters.RangeFilter(field_name=field.name)
            
#             elif field_type in ['DateField', 'DateTimeField']:
#                 # Para campos de fecha, agregar filtros de rango
#                 self.filters[field.name] = filters.DateFromToRangeFilter(field_name=field.name)
            
#             elif field_type == 'BooleanField':
#                 # Para campos booleanos, agregar filtro exacto
#                 self.filters[field.name] = filters.BooleanFilter(field_name=field.name)
            
#             elif field_type == 'ForeignKey':
#                 # Para claves foráneas, agregar filtro exacto por ID
#                 self.filters[field.name] = filters.NumberFilter(field_name=field.name, lookup_expr='exact')

#     class Meta:
#         model = Persona
#         fields = '__all__'  # Esto permite que todos los campos del modelo estén disponibles para el filtrado


class GenericDynamicFilter(filters.FilterSet):
    def __init__(self, *args, **kwargs):
        model = self.Meta.model
        if model is None:
            raise ValueError("Debe especificar un modelo en Meta.model.")

        # Inicializar el filtro normalmente
        super().__init__(*args, **kwargs)

        # Generar los filtros según el tipo de campo
        for field in model._meta.get_fields():
            if not hasattr(field, 'get_internal_type'):
                continue

            field_type = field.get_internal_type()

            if field_type in ['CharField', 'TextField']:
                self.filters[field.name] = filters.CharFilter(field_name=field.name, lookup_expr='icontains')
            elif field_type in ['IntegerField', 'FloatField', 'DecimalField']:
                self.filters[field.name] = filters.RangeFilter(field_name=field.name)
            elif field_type in ['DateField', 'DateTimeField']:
                self.filters[field.name] = filters.DateFromToRangeFilter(field_name=field.name)
            elif field_type == 'BooleanField':
                self.filters[field.name] = filters.BooleanFilter(field_name=field.name)
            elif field_type == 'ForeignKey':
                self.filters[field.name] = filters.NumberFilter(field_name=field.name, lookup_expr='exact')

    class Meta:
        model = None  # Se asignará dinámicamente en la vista específica
        fields = []   # No necesita campos específicos aquí

class DynamicModelFilter(filters.FilterSet):
    def __init__(self, *args, **kwargs):
        model = self.Meta.model
        if model is None:
            # No hacer nada si el modelo no está asignado todavía
            return super().__init__(*args, **kwargs)

        super().__init__(*args, **kwargs)

        # Generar filtros en función del tipo de campo del modelo
        for field in model._meta.get_fields():
            if not hasattr(field, 'get_internal_type'):
                continue

            field_type = field.get_internal_type()

            if field_type in ['CharField', 'TextField']:
                self.filters[field.name] = filters.CharFilter(field_name=field.name, lookup_expr='icontains')
            elif field_type in ['IntegerField', 'FloatField', 'DecimalField']:
                self.filters[field.name] = filters.RangeFilter(field_name=field.name)
            elif field_type in ['DateField', 'DateTimeField']:
                self.filters[field.name] = filters.DateFromToRangeFilter(field_name=field.name)
            elif field_type == 'BooleanField':
                self.filters[field.name] = filters.BooleanFilter(field_name=field.name)
            elif field_type == 'ForeignKey':
                self.filters[field.name] = filters.NumberFilter(field_name=field.name, lookup_expr='exact')

    class Meta:
        model = None  # Se asignará en cada ViewSet
        fields = []