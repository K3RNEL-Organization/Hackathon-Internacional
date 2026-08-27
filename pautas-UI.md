# Pautas de Interfaz de Usuario — TriageMed MVP

## 1. Propósito

Este documento define las pautas visuales, funcionales y de implementación UX/UI del MVP de **TriageMed**.

Su objetivo es que todos los integrantes del equipo puedan diseñar y desarrollar la interfaz de forma consistente, utilizando datos simulados durante la etapa inicial y manteniendo una estructura preparada para la integración posterior.

La interfaz debe priorizar:

* Claridad.
* Rapidez de interpretación.
* Accesibilidad.
* Consistencia visual.
* Diseño responsive.
* Identificación clara de niveles de prioridad.
* Jerarquización de información.
* Facilidad de implementación.

---

## 2. Objetivo principal de la interfaz

El usuario debe poder responder rápidamente:

1. ¿Existe una situación que requiere atención?
2. ¿Cuál es su nivel de prioridad?
3. ¿Dónde ocurre?
4. ¿Qué está ocurriendo?
5. ¿Cuándo fue detectada?
6. ¿Qué información respalda la clasificación?

La interfaz no debe obligar al usuario a interpretar grandes cantidades de información antes de comprender el estado general.

---

## 3. Principios UX/UI

### 3.1 Claridad antes que decoración

La interfaz debe priorizar la comprensión de la información por encima de los elementos decorativos.

```text
Información
    >
Interacción
    >
Decoración
```

Cada elemento visual debe cumplir una función relacionada con:

* Comprensión.
* Navegación.
* Identificación.
* Comparación.
* Toma de decisiones.

### 3.2 Jerarquía visual

La información más importante debe ser visible primero:

1. Estado general.
2. Casos de mayor prioridad.
3. Resumen de indicadores.
4. Información contextual.
5. Detalles secundarios.

### 3.3 Consistencia

Los mismos conceptos deben representarse siempre de la misma manera:

* Mismos colores.
* Mismos nombres.
* Mismos iconos.
* Mismos patrones de interacción.
* Mismos estilos de tarjetas y botones.

### 3.4 No depender únicamente del color

El color debe acompañarse siempre de texto, iconos o etiquetas descriptivas.

---

## 4. Arquitectura de vistas

El MVP debe priorizar las siguientes vistas:

```text
Dashboard
   │
   ├── Casos / Alertas
   │      │
   │      └── Detalle del caso
   │
   └── Indicadores
```

## 4.1 Dashboard

Es la pantalla principal de TriageMed.

Debe mostrar:

* Estado general.
* Casos activos.
* Distribución por nivel de prioridad.
* Indicadores principales.
* Tendencias.
* Última actualización.
* Casos recientes o prioritarios.

### Estructura recomendada

```text
Header
│
├── Identidad de TriageMed
├── Estado del sistema
└── Última actualización

Resumen
│
├── Casos totales
├── Prioridad crítica
├── Prioridad alta
├── Prioridad media
└── Prioridad baja

Indicadores
│
├── Gráfico o métrica principal
├── Tendencia
└── Valores relevantes

Casos recientes
│
└── Lista de CaseCard / AlertCard
```

## 4.2 Vista de casos o alertas

Debe mostrar una lista clara y escaneable de casos.

Cada elemento debe incluir:

* Nivel de prioridad.
* Título o motivo.
* Ubicación.
* Valor o indicador relevante.
* Fecha y hora.
* Estado.
* Acción para consultar el detalle.

## 4.3 Detalle del caso

Debe presentar la información de forma ordenada y fácil de leer.

La estructura debe responder:

```text
Qué → Dónde → Cuándo → Prioridad → Evidencia
```

---

## 5. Sistema de niveles de prioridad

Los niveles deben utilizar una escala visual consistente:

| Nivel    | Color base | Significado                        |
| -------- | ---------- | ---------------------------------- |
| LOW      | `#22C55E`  | Situación de baja prioridad        |
| MEDIUM   | `#EAB308`  | Situación que requiere seguimiento |
| HIGH     | `#F97316`  | Situación prioritaria              |
| CRITICAL | `#EF4444`  | Situación de máxima prioridad      |

### Representación visual

```text
● LOW
● MEDIUM
● HIGH
● CRITICAL
```

### CSS base

```css
.priority-indicator {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    display: inline-block;
}

.priority-low {
    background-color: #22C55E;
    box-shadow: 0 0 0 4px rgba(34, 197, 94, 0.12);
}

.priority-medium {
    background-color: #EAB308;
    box-shadow: 0 0 0 4px rgba(234, 179, 8, 0.12);
}

.priority-high {
    background-color: #F97316;
    box-shadow: 0 0 0 4px rgba(249, 115, 22, 0.12);
}

.priority-critical {
    background-color: #EF4444;
    box-shadow: 0 0 0 4px rgba(239, 68, 68, 0.12);
}
```

### Reglas

* El color debe acompañarse siempre de una etiqueta textual.
* No utilizar colores de prioridad como color general de la aplicación.
* La prioridad crítica debe tener mayor jerarquía visual.
* No utilizar animaciones agresivas para llamar la atención.

---

## 6. Paleta visual

> Actualizado: paleta de marca reemplazada por la variante teal/oscura (referencia: `index.html` / `styles.css` provistos). Los colores de prioridad NO cambian.

### 6.1 Colores funcionales

```text
LOW       #22C55E
MEDIUM    #EAB308
HIGH      #F97316
CRITICAL  #EF4444
```

### 6.2 Colores de interfaz

```text
Background (canvas)   #F5F8FB
Surface                #FFFFFF
Border (line)          #E2E8F0
Text Primary (ink)     #0F172A
Text Secondary (muted) #64748B
Text Muted (soft)      #94A3B8
```

### 6.3 Color de marca / acción

```text
Brand           #155E75
Brand Dark      #0E4658
Brand Soft      #E6F5F7
Sidebar bg      #073B4C   (fondo del sidebar, oscuro, distinto de Brand)
```

El color de marca (`Brand`) debe utilizarse para:

* Botones principales.
* Enlaces.
* Elementos activos (item de navegación activo, filtro activo).
* Selecciones.
* Indicadores interactivos.
* Estados de foco.

No utilizar los colores de prioridad como color principal de botones o navegación.

---

## 7. Tipografía

> Actualizado: dos familias, siguiendo `styles.css`.

* **Cuerpo / UI:** DM Sans.
* **Títulos / display (H1, H2, H3, marca, valores numéricos grandes):** Space Grotesk.

Ambas se cargan como Google Fonts.

### Jerarquía tipográfica

```text
H1       Título principal          Space Grotesk 600
H2       Título de sección         Space Grotesk 600
H3       Título de tarjeta         Space Grotesk 600
Body     Información general       DM Sans 400/500
Caption  Metadata y datos secundarios  DM Sans 400
```

### CSS base

```css
body {
    font-family: "DM Sans", system-ui, sans-serif;
    color: #0F172A;
    font-size: 14px;
}

h1, h2, h3, .brand strong, .kpi-card > strong {
    font-family: "Space Grotesk", system-ui, sans-serif;
}

h1 {
    font-size: 28px;
    font-weight: 600;
}

h2 {
    font-size: 20px;
    font-weight: 600;
}

h3 {
    font-size: 16px;
    font-weight: 600;
}

.caption {
    font-size: 12px;
    color: #64748B;
}
```

### Reglas

* Mantener una jerarquía clara.
* Evitar utilizar demasiados tamaños de fuente.
* No utilizar texto completamente en mayúsculas salvo para etiquetas breves.
* Garantizar contraste suficiente entre texto y fondo.

---

## 8. Sistema de espaciado

Utilizar múltiplos de 4px:

```text
4px
8px
12px
16px
24px
32px
48px
```

Evitar valores arbitrarios como:

```text
13px
17px
23px
37px
```

salvo que exista una razón específica de diseño.

---

## 9. Tarjetas

Las tarjetas deben utilizarse para agrupar información relacionada.

### Características

* Fondo blanco.
* Borde suave o sombra sutil.
* Radio entre 8px y 12px.
* Padding entre 16px y 24px.
* Jerarquía clara entre título, valor y metadata.
* Estados de hover y focus cuando sean interactivas.

### Ejemplo

```text
┌─────────────────────────────┐
│ CASOS ACTIVOS               │
│                             │
│ 18                          │
│ +12% respecto al período    │
└─────────────────────────────┘
```

### Reglas

* No sobrecargar una tarjeta con demasiada información.
* No utilizar sombras intensas.
* Mantener el mismo estilo en todas las vistas.
* Las tarjetas interactivas deben indicar visualmente que pueden seleccionarse.

---

## 10. Componente de prioridad

Crear un componente reutilizable para representar los niveles:

```text
PriorityBadge
```

Debe aceptar como mínimo:

```text
LOW
MEDIUM
HIGH
CRITICAL
```

### Ejemplo visual

```text
[ ● HIGH ]
```

### Reglas

* Mostrar indicador visual.
* Mostrar texto.
* Mantener tamaños consistentes.
* Utilizar nombres de clase semánticos.
* No duplicar estilos en cada vista.

---

## 11. Componente CaseCard / AlertCard

Cada caso debe poder identificarse rápidamente.

### Ejemplo

```text
┌────────────────────────────────────┐
│ ● HIGH                             │
│                                    │
│ Incremento de casos                │
│ Corrientes                         │
│                                    │
│ 27 eventos                         │
│ Hace 15 minutos                    │
│                                    │
│ Ver detalle                        │
└────────────────────────────────────┘
```

### Información mínima

* Nivel de prioridad.
* Título o motivo.
* Ubicación.
* Valor relevante.
* Fecha y hora.
* Estado.
* Acción para ver el detalle.

### Reglas

* El nivel debe ser visible sin abrir la tarjeta.
* El título debe ser breve y descriptivo.
* La ubicación debe estar claramente diferenciada.
* La acción debe tener un texto explícito.
* Toda la tarjeta puede ser interactiva si el patrón se mantiene consistente.

---

## 12. Vista de detalle

La vista de detalle debe organizar la información en bloques.

### Estructura recomendada

```text
Detalle del caso

[ HIGH ]

Incremento de casos

Ubicación
Corrientes

Fecha
27/08/2026 02:30

Indicador
Incremento de casos

Valor
27

Estado
Activo

Información adicional
...
```

### Orden de información

1. Nivel de prioridad.
2. Título o motivo.
3. Estado.
4. Ubicación.
5. Fecha y hora.
6. Indicadores.
7. Evidencia o información adicional.
8. Acciones disponibles.

### Reglas

* Evitar bloques extensos de texto sin separación.
* Utilizar etiquetas claras.
* Destacar los valores relevantes.
* Mantener visible la acción para volver a la lista.
* No ocultar información esencial detrás de interacciones innecesarias.

---

## 13. Jerarquía visual del Dashboard

El Dashboard debe organizarse de la siguiente manera:

```text
1. Estado general
2. Casos críticos
3. Resumen de casos
4. Indicadores
5. Tendencias
6. Información secundaria
```

Una prioridad `CRITICAL` no debe quedar visualmente escondida debajo de elementos secundarios.

---

## 14. Gráficos e indicadores

Los gráficos deben utilizarse únicamente cuando faciliten la interpretación.

### Preferir

* Gráficos de líneas.
* Gráficos de barras.
* Donuts simples.
* Indicadores numéricos.
* Comparaciones directas.

### Evitar

* Gráficos 3D.
* Decoración innecesaria.
* Demasiadas series.
* Exceso de colores.
* Etiquetas ilegibles.
* Gráficos sin una pregunta clara.

Cada gráfico debe responder una pregunta concreta:

```text
¿Los casos están aumentando?
→ Gráfico temporal.

¿Qué nivel de prioridad predomina?
→ Distribución por niveles.

¿Qué ubicación concentra más casos?
→ Comparación por ubicación.
```

---

## 15. Estados de interfaz

Todos los componentes que dependan de datos deben contemplar los siguientes estados.

### Loading

```text
Cargando información...
```

Utilizar skeletons o indicadores discretos cuando sea posible.

### Empty

```text
No hay casos activos.
```

El estado vacío debe explicar la situación y no dejar la pantalla en blanco.

### Error

```text
No se pudo cargar la información.
Intentar nuevamente.
```

El mensaje debe ser claro y ofrecer una acción de recuperación cuando corresponda.

### Success

Mostrar la información normalmente.

### Reglas

* No dejar contenedores vacíos sin explicación.
* Mantener la estructura visual durante la carga.
* Evitar mensajes técnicos para usuarios finales.
* Utilizar mensajes consistentes en toda la aplicación.

---

## 16. Responsive Design

La interfaz debe funcionar correctamente en:

```text
Desktop
Tablet
Mobile
```

### Desktop

* Dashboard con varias columnas.
* Sidebar visible si corresponde.
* Tarjetas distribuidas en grids.
* Gráficos con espacio suficiente.

### Tablet

* Reducir la cantidad de columnas.
* Mantener la jerarquía visual.
* Ajustar tamaños y espacios.
* Evitar que las tarjetas pierdan legibilidad.

### Mobile

```text
Sidebar
↓
Menú o navegación compacta

Grid
↓
Columna

Tabla
↓
Tarjetas o lista desplazable
```

### Reglas

* Las tarjetas no deben romperse horizontalmente.
* Los textos importantes no deben truncarse sin alternativa.
* Los botones deben tener un área táctil adecuada.
* Las acciones principales deben permanecer visibles.
* Evitar scroll horizontal innecesario.

---

## 17. Accesibilidad

La interfaz debe cumplir principios básicos de accesibilidad:

* Contraste suficiente.
* Textos legibles.
* No depender únicamente del color.
* Estados claramente identificables.
* Botones con nombres descriptivos.
* Navegación mediante teclado cuando corresponda.
* Uso de HTML semántico.
* `alt` en imágenes relevantes.
* Estados de foco visibles.
* Etiquetas asociadas a campos de formulario.

### Ejemplo

```html
<button aria-label="Ver detalle del caso">
    Ver detalle
</button>
```

### Reglas adicionales

* No utilizar únicamente iconos para acciones importantes.
* No utilizar texto demasiado pequeño para información esencial.
* Mantener una estructura lógica de encabezados.
* Asegurar que los elementos interactivos sean distinguibles.

---

## 18. Iconografía

Utilizar un único sistema de iconos en toda la interfaz.

### Reglas

* No mezclar estilos visuales.
* Utilizar iconos como complemento del texto.
* No reemplazar etiquetas importantes únicamente por iconos.
* Mantener tamaños y alineaciones consistentes.
* Utilizar `aria-label` cuando un icono sea interactivo.

Ejemplo recomendado:

```text
⚠ HIGH
```

En lugar de utilizar únicamente:

```text
⚠
```

---

## 19. Microinteracciones

Las animaciones deben ser discretas y funcionales.

### Permitidas

* Hover.
* Focus.
* Transiciones suaves.
* Cambios de estado.
* Indicadores de carga.
* Apertura y cierre de paneles.

### Evitar

* Animaciones constantes.
* Parpadeos.
* Efectos excesivos.
* Transiciones lentas.
* Elementos que distraigan de la información principal.

Una prioridad crítica debe destacarse mediante jerarquía visual, contraste y ubicación, no mediante animaciones agresivas.

---

## 20. Navegación

La navegación debe ser simple y predecible.

> Actualizado: la navegación principal vive en un **sidebar fijo** a la izquierda (desktop), no en un header horizontal. En mobile el sidebar se oculta y se abre con un botón de menú (☰) en el topbar.

### Estructura recomendada

```text
Sidebar
├── Marca (logo)
├── Dashboard
├── Pacientes
├── Señales
└── Footer: estado del sistema + perfil del usuario / cerrar sesión

Topbar (por página)
├── Botón de menú (solo mobile)
├── Breadcrumb / título de sección
└── Acciones contextuales (ej. Actualizar)
```

### Reglas

* Mantener visible la sección activa (resaltada en el sidebar).
* Utilizar nombres claros.
* Evitar menús innecesariamente profundos.
* Permitir volver fácilmente desde el detalle a la lista.
* Mantener la navegación consistente en desktop y mobile (sidebar off-canvas en mobile, no un menú de tres puntos independiente).

---

## 21. Arquitectura de componentes UI

Se recomienda una estructura similar:

```text
src/
│
├── components/
│   ├── PriorityBadge/
│   ├── CaseCard/
│   ├── StatCard/
│   ├── Header/
│   ├── Sidebar/
│   ├── StatusIndicator/
│   ├── Chart/
│   └── EmptyState/
│
├── pages/
│   ├── Dashboard/
│   ├── Cases/
│   └── CaseDetail/
│
├── data/
│   └── mockData.js
│
├── styles/
│   ├── variables.css
│   ├── global.css
│   └── responsive.css
│
└── App
```

### Reglas

* Crear componentes reutilizables.
* Evitar duplicar estilos.
* Mantener nombres semánticos.
* Separar componentes visuales de las páginas.
* Mantener una única fuente de verdad para colores y variables visuales.

---

## 22. Variables visuales

Centralizar los valores visuales en variables CSS:

```css
:root {
    --color-background: #F5F8FB;
    --color-surface: #FFFFFF;
    --color-border: #E2E8F0;

    --color-text-primary: #0F172A;
    --color-text-secondary: #64748B;
    --color-text-muted: #94A3B8;

    --color-low: #22C55E;
    --color-medium: #EAB308;
    --color-high: #F97316;
    --color-critical: #EF4444;

    --color-brand: #155E75;
    --color-brand-dark: #0E4658;
    --color-brand-soft: #E6F5F7;
    --color-sidebar-bg: #073B4C;

    --radius-sm: 8px;
    --radius-md: 12px;

    --space-1: 4px;
    --space-2: 8px;
    --space-3: 12px;
    --space-4: 16px;
    --space-5: 24px;
    --space-6: 32px;
    --space-7: 48px;
}
```

### 22.1 Componentes nuevos (referencia visual)

Agregados a partir del mockup `index.html` / `styles.css` (mismos principios de la sección 9, adaptados):

* **KpiCard**: variante de `StatCard` con un ícono en la esquina superior derecha (color según el tipo de métrica, no según prioridad). Solo debe usarse para valores reales provistos por el backend — no agregar métricas ni variaciones de tendencia (`+8.2%`, etc.) que no existan en los datos.
* **PriorityDistributionBar**: barra horizontal segmentada + leyenda, construida a partir de los conteos reales de prioridad (igual fuente de datos que las `KpiCard` de prioridad del Dashboard).
* **CaseCard**: evolución de `CaseCard`/`PatientSignalCard` con borde izquierdo de 3px del color de la prioridad, en vez de solo el punto indicador.
* **Sidebar / Topbar**: reemplazan al `Header` horizontal. Ver sección 20.

### Reglas

* No inventar íconos o métricas que sugieran datos que el backend no provee.
* Mantener el mismo componente `PriorityBadge` (punto + texto) dentro de las tarjetas nuevas.

---

## 23. Datos simulados para desarrollo visual

Durante el desarrollo de las pantallas se pueden utilizar datos simulados.

Ubicación recomendada:

```text
src/
└── data/
    └── mockData.js
```

Ejemplo:

```js
export const mockCases = [
    {
        id: "CASE-001",
        priority: "HIGH",
        title: "Incremento de casos",
        location: "Corrientes",
        value: 27,
        status: "active",
        timestamp: "2026-08-27T02:30:00"
    },
    {
        id: "CASE-002",
        priority: "MEDIUM",
        title: "Variación del indicador",
        location: "Resistencia",
        value: 14,
        status: "active",
        timestamp: "2026-08-27T02:15:00"
    }
];
```

Los datos simulados deben permitir probar:

* Casos de todos los niveles.
* Estados activos e inactivos.
* Listas vacías.
* Textos largos.
* Valores altos y bajos.
* Fechas diferentes.
* Estados de error y carga.

---

## 24. Separación entre UI y lógica

Los componentes visuales no deben contener lógica compleja de negocio.

### Evitar

```text
CaseCard
    ↓
calcula prioridad
    ↓
determina clasificación
    ↓
renderiza resultado
```

### Preferir

```text
Datos preparados
    ↓
Componente visual
    ↓
Renderización
```

Los componentes deben enfocarse en:

* Presentación.
* Interacción.
* Navegación.
* Estados visuales.
* Accesibilidad.

La lógica de clasificación o procesamiento no debe implementarse dentro de los componentes visuales.

---

## 25. Reglas de contenido

### Textos

* Utilizar lenguaje claro y directo.
* Evitar tecnicismos innecesarios.
* Mantener títulos breves.
* Utilizar etiquetas consistentes.
* Evitar mensajes ambiguos.

### Fechas

Utilizar un formato consistente en toda la aplicación:

```text
27/08/2026 02:30
```

### Estados

Utilizar nombres consistentes:

```text
Activo
Inactivo
Pendiente
Resuelto
```

### Acciones

Preferir textos explícitos:

```text
Ver detalle
Volver a casos
Intentar nuevamente
Aplicar filtro
Limpiar filtros
```

---

## 26. Flujo principal del usuario

El flujo principal debe ser:

```text
Dashboard
    ↓
Detecta caso prioritario
    ↓
Identifica nivel
    ↓
Consulta ubicación e indicador
    ↓
Abre el caso
    ↓
Consulta el detalle
```

El usuario debe poder llegar al detalle con el mínimo número de interacciones razonables.

---

## 27. Prioridades de implementación UX/UI

### P0 — Obligatorio

* Dashboard.
* Sistema visual de prioridades.
* Lista de casos.
* Detalle del caso.
* Navegación básica.
* Diseño responsive.
* Estados loading, empty y error.
* Componentes reutilizables.
* Consistencia visual.
* Accesibilidad básica.

### P1 — Si existe tiempo

* Gráficos.
* Filtros.
* Búsqueda.
* Ordenamiento.
* Animaciones sutiles.
* Mejoras de accesibilidad.
* Estados avanzados de interacción.

### P2 — Fuera del MVP inicial

* Personalización avanzada.
* Temas visuales.
* Configuración extensa.
* Dashboards personalizables.
* Animaciones complejas.
* Funcionalidades administrativas no esenciales.

---

## 28. Flujo de implementación recomendado

```text
1. Definir variables visuales
        ↓
2. Crear componentes base
        ↓
3. Crear PriorityBadge
        ↓
4. Crear StatCard
        ↓
5. Crear CaseCard
        ↓
6. Construir Dashboard
        ↓
7. Construir lista de casos
        ↓
8. Construir detalle del caso
        ↓
9. Agregar estados loading/empty/error
        ↓
10. Agregar responsive
        ↓
11. Revisar accesibilidad
        ↓
12. Probar flujo completo
```

---

## 29. Criterios de aceptación UX/UI

La interfaz se considera lista para el MVP cuando:

* [ ] El Dashboard presenta claramente el estado general.
* [ ] Los niveles LOW, MEDIUM, HIGH y CRITICAL son distinguibles.
* [ ] Cada nivel incluye color y texto.
* [ ] Los casos pueden visualizarse en una lista.
* [ ] Un caso puede abrirse para consultar su detalle.
* [ ] La información principal es comprensible rápidamente.
* [ ] La navegación es clara y consistente.
* [ ] Existe una versión responsive.
* [ ] Existen estados de loading, empty y error.
* [ ] Los componentes principales son reutilizables.
* [ ] La interfaz mantiene una paleta visual consistente.
* [ ] Los textos y acciones son claros.
* [ ] Los elementos interactivos tienen estados hover y focus.
* [ ] La interfaz no depende únicamente del color.
* [ ] No existen elementos visuales innecesarios que dificulten la lectura.
* [ ] Los casos críticos tienen mayor jerarquía visual.
* [ ] La interfaz puede probarse con datos simulados.
* [ ] La estructura de carpetas y componentes está documentada.

---

## 30. Estructura recomendada para la documentación UI

```text
pautas-ui/
├── README.md
├── componentes.md
├── colores.md
├── tipografia.md
├── responsive.md
└── assets/
```

El archivo `README.md` debe ser la referencia principal para cualquier integrante que implemente o modifique la interfaz de TriageMed.

---

## Principio final

La interfaz de TriageMed debe ser:

* Simple.
* Profesional.
* Informativa.
* Accionable.
* Accesible.
* Consistente.
* Fácil de interpretar.

El diseño debe ayudar al usuario a pasar rápidamente de:

```text
Caso
  ↓
Prioridad
  ↓
Contexto
  ↓
Detalle
  ↓
Decisión
```

La prioridad del equipo debe ser construir una interfaz clara y funcional antes de agregar elementos visuales secundarios.
