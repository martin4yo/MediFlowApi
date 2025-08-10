# 📊 MediFlow API - Sistema Financiero

## 🎯 Resumen del Sistema

El sistema financiero de MediFlow maneja todo el flujo económico de los consultorios médicos, desde la reserva de turnos con señas hasta las liquidaciones a profesionales.

### 🔄 Flujo Financiero Completo:
1. **Paciente reserva turno** → Cálculo automático de precios
2. **Pago de seña** (opcional) → Registro en caja
3. **Consulta médica** → Pago del resto o total
4. **Liquidación mensual** → Cálculo de comisiones
5. **Pago a profesional** → Egreso de caja
6. **Reportes y balances** → Control financiero

---

## 💰 API de Pagos

### Endpoints Base: `/api/financieros/pago/`

#### Crear Pago
```http
POST /api/financieros/pago/
Content-Type: application/json

{
    "idturno": 1,
    "tipo_pago": "SENA",
    "metodo_pago": "EFECTIVO", 
    "monto": 2400.00,
    "comprobante": "REC-001",
    "observaciones": "Seña 30% de consulta"
}
```

**Tipos de pago disponibles:**
- `SENA` - Seña del turno
- `RESTO` - Resto del pago (después de seña)
- `COMPLETO` - Pago completo sin seña
- `REEMBOLSO` - Reembolso por cancelación

**Métodos de pago:**
- `EFECTIVO`, `TARJETA_DEBITO`, `TARJETA_CREDITO`, `TRANSFERENCIA`, `MERCADOPAGO`

#### Confirmar Pago
```http
POST /api/financieros/pago/{id}/confirmar/
```

#### Anular Pago
```http
POST /api/financieros/pago/{id}/anular/
{
    "motivo": "Error en el monto registrado"
}
```

#### Reportes de Pagos

**Resumen Diario:**
```http
GET /api/financieros/pago/resumen_diario/?fecha=2024-02-15&centro_id=1
```

**Pagos por Turno:**
```http
GET /api/financieros/pago/por_turno/?turno_id=123
```

**Estadísticas:**
```http
GET /api/financieros/pago/estadisticas/?centro_id=1&fecha_desde=2024-02-01&fecha_hasta=2024-02-29
```

---

## 🏢 API de Configuración de Comisiones

### Endpoints Base: `/api/financieros/configuracioncomision/`

#### Crear Configuración
```http
POST /api/financieros/configuracioncomision/
{
    "idprofesional": 1,
    "idcentro": 1,
    "porcentaje_profesional": 75.00,
    "porcentaje_centro": 25.00,
    "fecha_inicio": "2024-02-01",
    "descripcion": "Comisión especial para Dr. Pérez"
}
```

#### Obtener Comisión Aplicable
```http
GET /api/financieros/configuracioncomision/obtener_comision/?profesional_id=1&centro_id=1&especialidad_practica_id=1&fecha=2024-02-15
```

**Respuesta:**
```json
{
    "configuracion_encontrada": true,
    "configuracion": {
        "porcentaje_profesional": 75.00,
        "porcentaje_centro": 25.00,
        "descripcion": "Comisión especial para Dr. Pérez"
    }
}
```

---

## 📋 API de Liquidaciones

### Endpoints Base: `/api/financieros/liquidacion/`

#### Crear Liquidación
```http
POST /api/financieros/liquidacion/
{
    "idprofesional": 1,
    "idcentro": 1,
    "periodo_desde": "2024-02-01",
    "periodo_hasta": "2024-02-29",
    "descuentos": 5000.00,
    "observaciones": "Liquidación febrero 2024"
}
```

#### Calcular Liquidación
```http
POST /api/financieros/liquidacion/{id}/calcular/
```
*Calcula automáticamente todos los montos basándose en los pagos del período*

#### Aprobar Liquidación
```http
POST /api/financieros/liquidacion/{id}/aprobar/
```

#### Marcar como Pagada
```http
POST /api/financieros/liquidacion/{id}/marcar_pagada/
```
*Automáticamente crea el movimiento de caja correspondiente*

#### Liquidación Masiva
```http
POST /api/financieros/liquidacion/crear_masiva/
{
    "profesionales_ids": [1, 2, 3],
    "centro_id": 1,
    "periodo_desde": "2024-02-01",
    "periodo_hasta": "2024-02-29"
}
```

#### Resumen por Período
```http
GET /api/financieros/liquidacion/resumen_periodo/?centro_id=1&periodo_desde=2024-02-01&periodo_hasta=2024-02-29
```

---

## 📊 API de Gastos Administrativos

### Endpoints Base: `/api/financieros/gastoadministrativo/`

#### Crear Gasto
```http
POST /api/financieros/gastoadministrativo/
{
    "idcentro": 1,
    "categoria": "SERVICIOS",
    "subcategoria": "Electricidad",
    "concepto": "Factura EDESUR Febrero 2024",
    "proveedor": "EDESUR",
    "monto": 25000.00,
    "iva": 5250.00,
    "fecha_gasto": "2024-02-15",
    "fecha_vencimiento": "2024-03-15",
    "es_recurrente": true
}
```

**Categorías disponibles:**
- `SERVICIOS`, `ALQUILER`, `EQUIPAMIENTO`, `MANTENIMIENTO`, `PERSONAL`, `IMPUESTOS`, `SEGUROS`, `MARKETING`, `MATERIALES`, `LIMPIEZA`, `SISTEMAS`

#### Marcar como Pagado
```http
POST /api/financieros/gastoadministrativo/{id}/marcar_pagado/
{
    "fecha_pago": "2024-02-20",
    "metodo_pago": "TRANSFERENCIA"
}
```

#### Reportes de Gastos

**Gastos Vencidos:**
```http
GET /api/financieros/gastoadministrativo/vencidos/?centro_id=1
```

**Por Vencer:**
```http
GET /api/financieros/gastoadministrativo/por_vencer/?centro_id=1&dias=7
```

**Resumen Mensual:**
```http
GET /api/financieros/gastoadministrativo/resumen_mensual/?centro_id=1&ano=2024&mes=2
```

---

## 💸 API de Movimientos de Caja

### Endpoints Base: `/api/financieros/movimientocaja/`

#### Saldo Actual
```http
GET /api/financieros/movimientocaja/saldo_actual/?centro_id=1
```

**Respuesta:**
```json
{
    "centro_id": 1,
    "fecha_consulta": "actual",
    "saldo": 285750.50
}
```

#### Flujo Diario
```http
GET /api/financieros/movimientocaja/flujo_diario/?centro_id=1&fecha=2024-02-15
```

**Respuesta:**
```json
{
    "fecha": "2024-02-15",
    "saldo_inicial": 250000.00,
    "saldo_final": 285750.50,
    "ingresos": {
        "total": 45000.00,
        "cantidad": 6
    },
    "egresos": {
        "total": 9250.00,
        "cantidad": 2
    },
    "movimientos": [...]
}
```

#### Reporte Mensual
```http
GET /api/financieros/movimientocaja/reporte_mensual/?centro_id=1&ano=2024&mes=2
```

#### Balance General
```http
GET /api/financieros/movimientocaja/balance_general/?centro_id=1&fecha_hasta=2024-02-29
```

**Respuesta:**
```json
{
    "centro_id": 1,
    "fecha_corte": "2024-02-29",
    "resumen": {
        "total_ingresos": 450000.00,
        "total_egresos": 125000.00,
        "saldo_final": 325000.00
    },
    "detalle_ingresos": [...],
    "detalle_egresos": [...]
}
```

---

## 🎫 API de Turnos (Integración Financiera)

### Endpoints Base: `/api/turnos/turno/`

Los turnos se integran automáticamente con el sistema financiero:

#### Crear Turno
```http
POST /api/turnos/turno/
{
    "idpaciente": 1,
    "idprofesional": 1,
    "idcentro": 1,
    "idespecialidadpractica": 1,
    "fecha": "2024-02-20",
    "hora": "14:30",
    "observaciones_paciente": "Primera consulta"
}
```

*Al crear el turno, automáticamente se calculan los precios basándose en la práctica y cobertura del paciente.*

**Campos financieros automáticos en respuesta:**
```json
{
    "id": 123,
    "precio_total": 8000.00,
    "precio_cobertura": 5600.00,
    "precio_paciente": 2400.00,
    "sena_requerida": 720.00,
    "sena_pagada": false,
    "pago_completo": false,
    "saldo_pendiente": 2400.00
}
```

---

## 🔧 Configuración Inicial Requerida

### 1. Estados de Turno
Ejecutar: `python crear_datos_iniciales.py`

### 2. Configuración de Comisiones
```http
POST /api/financieros/configuracioncomision/
{
    "porcentaje_profesional": 70.00,
    "porcentaje_centro": 30.00,
    "fecha_inicio": "2024-01-01",
    "descripcion": "Configuración por defecto"
}
```

### 3. Precios de Prácticas
Configurar `precio_base` en cada práctica médica.

---

## 🚀 Casos de Uso Ejemplo

### Flujo Completo: Turno con Seña

#### 1. Crear Turno
```http
POST /api/turnos/turno/
{
    "idpaciente": 1,
    "idprofesional": 1,
    "idcentro": 1,
    "idespecialidadpractica": 1,
    "fecha": "2024-02-20",
    "hora": "14:30"
}
```

#### 2. Pagar Seña
```http
POST /api/financieros/pago/
{
    "idturno": 123,
    "tipo_pago": "SENA",
    "metodo_pago": "EFECTIVO",
    "monto": 720.00
}
```

#### 3. Pagar Resto (día de la consulta)
```http
POST /api/financieros/pago/
{
    "idturno": 123,
    "tipo_pago": "RESTO",
    "metodo_pago": "TARJETA_DEBITO",
    "monto": 1680.00
}
```

#### 4. Liquidación Mensual
```http
POST /api/financieros/liquidacion/
{
    "idprofesional": 1,
    "idcentro": 1,
    "periodo_desde": "2024-02-01",
    "periodo_hasta": "2024-02-29"
}

POST /api/financieros/liquidacion/{id}/calcular/
POST /api/financieros/liquidacion/{id}/aprobar/
POST /api/financieros/liquidacion/{id}/marcar_pagada/
```

---

## ⚠️ Validaciones Automáticas

- **Pagos**: No se puede pagar resto sin seña previa
- **Turnos**: No se puede agendar en horarios ocupados
- **Comisiones**: Los porcentajes deben sumar 100%
- **Saldos**: Control automático de saldos pendientes
- **Estados**: Flujo de estados validado en cada operación

---

## 📈 Reportes Disponibles

1. **Resúmenes Diarios** - Ingresos por día y centro
2. **Estadísticas de Pagos** - Por método, tipo y período  
3. **Gastos por Categoría** - Control de egresos administrativos
4. **Liquidaciones por Período** - Comisiones por profesional
5. **Balance General** - Estado financiero completo
6. **Flujo de Caja** - Movimientos detallados por período

---

*Sistema desarrollado con Django REST Framework*  
*Versión: 2.0 - Febrero 2024*