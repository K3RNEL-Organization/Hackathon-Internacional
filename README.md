# TriageMed — HealthSignal LATAM / RISA Data V1.0

TriageMed es un sistema de detección temprana y priorización de señales a partir de datos multifuente, desarrollado para el desafío HealthSignal LATAM.

El objetivo del sistema no es realizar diagnósticos clínicos, sino detectar desviaciones relevantes respecto del comportamiento basal de cada paciente, priorizarlas y entregar evidencia trazable disponible al momento de la decisión.

---

## Pipeline principal

El pipeline principal se encuentra en:

```text
src/risk/run_pipeline_v03.py
```

Ejecutar desde la raíz del proyecto:

```bash
python src/risk/run_pipeline_v03.py
```

---

## Fuentes utilizadas

El motor integra:

- `vital_signs.csv`
- `wearable_observations.csv`
- `device_observations.csv`
- `patient_context.csv`
- `connectivity_events.csv`
- `laboratory_results.csv`

---

## Flujo del sistema

```text
RAW
↓
Validación y normalización
↓
Timeline temporal
↓
Baseline personal
↓
Ventanas temporales
↓
Detección de desviaciones
↓
Persistencia
↓
Contexto y calidad
↓
Risk Score
↓
Priorización
↓
Evidencia trazable
↓
signals.csv + evidence.csv
```

---

## Baseline personal

Para cada paciente se utilizan las primeras 24 horas de datos válidos como período inicial de calibración.

Se calcula para cada variable:

- media
- mediana
- desviación estándar

Variables utilizadas:

- HR
- RR
- SpO2
- TEMP
- SBP
- DBP

---

## Detección

El sistema analiza ventanas temporales de 4 horas con decisiones cada 1 hora.

Se calcula la desviación respecto del baseline personal mediante z-score.

Una ventana candidata requiere:

- `|z-score| >= 2`
- al menos 2 variables desviadas

Para confirmar una señal se requieren al menos 2 ventanas consecutivas.

Estos parámetros son decisiones del MVP y no representan umbrales clínicos oficiales.

---

## Risk Score

El risk score combina:

- magnitud de la desviación
- cantidad de variables afectadas
- persistencia temporal
- calidad del dispositivo
- contexto de actividad

El score se encuentra entre 0 y 1.

Prioridades:

- LOW: `< 0.30`
- MEDIUM: `0.30 - 0.49`
- HIGH: `0.50 - 0.74`
- CRITICAL: `>= 0.75`

Estas categorías forman parte del modelo de priorización del MVP.

---

## Temporalidad

El pipeline respeta event time y availability time.

Ejemplos:

- Vital signs:
  - event time = `timestamp`
  - availability time = `timestamp`
- Wearables:
  - event time = `timestamp`
  - availability time = `sync_datetime`
- Laboratorios:
  - event time = `sample_datetime`
  - availability time = `result_datetime`

Ninguna evidencia puede utilizarse si todavía no estaba disponible al momento de la decisión.

---

## Contexto

### Actividad wearable

Permite contextualizar desviaciones asociadas a actividad física.

### Patient context

Incluye información temporal de sueño y recuperación.

Se exige una superposición temporal mínima de 15 minutos con la ventana de evidencia.

### Conectividad

Permite identificar eventos:

- DISCONNECTED
- INTERMITTENT
- DELAYED_SYNC

Los problemas de conectividad se utilizan como evidencia de calidad y no como señales clínicas.

### Laboratorios

Los resultados disponibles durante la ventana se agregan como evidencia `SUPPORTING`.

Los límites `reference_low` y `reference_high` se utilizan únicamente como contexto y no como thresholds automáticos de riesgo.

---

## Resultados actuales

El pipeline v0.3 procesa:

- 1000 pacientes
- 461 señales
- 300 pacientes con al menos una señal
- 16152 registros de evidencia

Distribución de prioridades:

- MEDIUM: 361
- HIGH: 86
- CRITICAL: 14

---

## Archivos generados

### `results/signals.csv`

Una fila por señal detectada.

Incluye:

- `signal_id`
- `patient_id`
- `decision_datetime`
- `risk_score`
- `priority_level`
- `confidence_score`
- `evidence_start`
- `evidence_end`
- `explanation`
- `model_version`

### `results/evidence.csv`

Contiene los registros que justifican o contextualizan cada señal.

Roles:

- `PRIMARY`
- `SUPPORTING`
- `CONTEXT`
- `QUALITY`

---

## Validaciones

El pipeline comprueba:

- `signal_id` duplicados
- señales sin evidencia
- evidencia disponible después de la decisión
- risk scores fuera de rango

Resultado actual:

- 0 `signal_id` duplicados
- 0 señales sin evidencia
- 0 evidencias futuras
- 0 risk scores inválidos

El resultado también fue validado mediante el Submission Validator oficial de RISA con 0 warnings.

---

## Auditorías realizadas

Se realizaron auditorías específicas sobre:

- señales CRITICAL
- contexto temporal
- conectividad
- laboratorios

La auditoría de laboratorios verificó:

- `result_datetime <= decision_datetime`
- `available_datetime = result_datetime`
- `event_datetime = sample_datetime`
- correspondencia con registros originales

Resultado:

```text
AUDITORIA LABS: PASS
```

---

## Integración con dashboard

El dashboard puede consumir directamente:

```text
results/signals.csv
results/evidence.csv
```

Vista sugerida:

```text
Resumen de señales
↓
Filtros por prioridad y paciente
↓
Tabla ordenada por risk_score
↓
Detalle de señal
↓
Explicación + evidencia asociada
```

---

## Versión

Modelo actual:

```text
risa_mvp_v0.3
```
