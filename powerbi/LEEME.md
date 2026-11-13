# Power BI: qué conservar, qué ajustar y qué falta en «Tablero Vertedero»

Esta guía parte del avance que ya tiene `Tablero Vertedero.pbix` (guardado el 7 de noviembre de 2026). El archivo tiene 3 páginas con 18 visuales y una tabla `Medidas` con 12 medidas. La lista sale de leer el propio archivo:

- **Medidas que ya existen:** `Llenado actual %`, `Llenado promedio %`, `Lecturas`, `% lecturas válidas`, `Aperturas`, `Bloqueos por caneca llena`, `Alarmas`, `Horas en alarma`, `Peso actual (g)`, `Peso promedio (g)`, `Peso máximo (g)` y `Gramos por punto de llenado`.

La mayor parte del dashboard ya está hecha. Para cumplir el punto 3 de la guía y coincidir con el sitio hay que:

- ajustar títulos y algunos campos de lo que ya existe;
- agregar **5 visuales nuevos**.

## 1. Lo que ya tienen

| Página | Visual existente | Qué hacer | Cumple en el sitio |
|---|---|---|---|
| Estado actual | 3 medidores `[Llenado actual %]` (C1, C2, C3) | **Conservar.** Corregir títulos: `C1 · Aprovechables`, `C2 · No aprovechables`, `C3 · Orgánicos` (sin punto final). | Estado en vivo |
| Estado actual | Tarjeta: `Peso actual (g)`, `% lecturas válidas`, `Horas en alarma`, `Alarmas` | **Conservar.** Renombrar el campo de peso a «Peso simulado (g)». | Apoyo |
| Estado actual | Segmentaciones de fecha y caneca | **Conservar.** | Filtros |
| Page 1 | Barras: `[Bloqueos por caneca llena]` por caneca | **Conservar.** Título: «Bloqueos por caneca (cantidad)». | Apoyo del indicador 4 |
| Page 1 | Columnas: `[Aperturas]` por `hora_texto`, con leyenda por caneca | **Ajustar:** quitar `DimCaneca[nombre]` de Leyenda. Título: «Aperturas por hora del día (cantidad)». | **Univariado 3** |
| Page 1 | Líneas «Llenado promedio por hora.» (leyenda por caneca) | **Conservar.** Título: «Llenado promedio por hora y caneca (%)». | **Bivariado 3** |
| Page 1 | Líneas «Llenado promedio por día.» | **Conservar.** Título: «Llenado promedio por día y caneca (%)». | Apoyo (tendencia) |
| Page 1 | Matriz: `[Aperturas]` por día de la semana × franja | **Conservar.** Título: «Aperturas por día de la semana y franja (cantidad)». | Apoyo de la decisión 2 |
| Page 1 | Segmentaciones de fecha y caneca | **Conservar.** Agregar una de `DimFecha[tipo_dia]`. | Filtros |
| Page 2 | Columnas: `[Alarmas]` por día de la semana | **Reutilizar** para el bivariado 2 (ver abajo): con solo 3 alarmas este gráfico no informa mucho. | **Bivariado 2** |
| Page 2 | Tarjeta: `[Alarmas]`, `[Horas en alarma]` | **Ajustar:** agregar `[Horas promedio de alarma]`. Título: «Alarmas conjuntas y duración (h)». | **Indicador 5** |
| Page 2 | Tabla de alarmas | **Ajustar:** quitar las jerarquías de fecha (en cada campo de fecha, flecha → elegir `fecha_inicio`/`fecha_fin` en vez de «Jerarquía de fechas») y poner `pct_c1..3` en «No resumir». Título: «Alarmas conjuntas: inicio, fin, duración (min) y llenado (%)». | Apoyo del indicador 5 |
| Page 2 | Anillo: `[Lecturas]` por estado de llenado | **Conservar.** Título: «Lecturas por estado de llenado (% de las lecturas)». | Apoyo del indicador 2 |
| Page 2 | Dispersión llenado–peso, tarjeta «Gramos por punto», columnas «Peso máximo» | **Opcional.** El peso es simulado y se calcula a partir del llenado, así que no aporta a los conocimientos. Si los conservan, titúlenlos con «Peso simulado (g)». | — |

## 2. Antes de lo nuevo

- **Renombrar páginas** (doble clic en la pestaña): «Page 1» → `Uso y llenado`; «Page 2» → `Bloqueos y alarmas`.
- **Filtro de período** en «Uso y llenado» y «Bloqueos y alarmas»:
  1. Abrir el panel Filtros y, en «Filtros de esta página», arrastrar `DimFecha[fecha]`.
  2. Elegir «Filtrado avanzado → es posterior o igual a 27/09/2026 y es anterior o igual a 04/11/2026».
  3. «Estado actual» **no** lleva este filtro.
- **Subtítulo** de los visuales de esas dos páginas: `Período simulado: 27 sep – 4 nov 2026` (Formato → General → Título → Subtítulo).
- **Ordenar** `DimHora[hora_texto]` por `hora_key` y `DimFecha[nombre_dia]` por `dia_semana` (vista Datos → seleccionar la columna → Herramientas de columnas → Ordenar por columna).
- **Medidas nuevas** (clic derecho en la tabla `Medidas` → Nueva medida, una por una):

```DAX
Intentos = CALCULATE ( SUM ( FactEventos[cantidad] ), DimTipoEvento[tipo] IN { "apertura", "bloqueo_llena" } )
Tasa de bloqueo % = DIVIDE ( [Bloqueos por caneca llena], [Intentos] ) * 100
Días con datos = DISTINCTCOUNT ( FactLecturas[fecha_key] )
Aperturas por día = DIVIDE ( [Aperturas], [Días con datos] )
% lecturas ≥ 90 = DIVIDE ( CALCULATE ( COUNTROWS ( FactLecturas ), FactLecturas[porcentaje] >= 90 ), COUNTROWS ( FactLecturas ) ) * 100
Mediana de llenado % = MEDIAN ( FactLecturas[porcentaje] )
Horas promedio de alarma = DIVIDE ( SUM ( FactAlarmas[duracion_min] ), 60 * COUNTROWS ( FactAlarmas ) )
```

- **Columna nueva** en `FactLecturas`, para el histograma (vista Datos → `FactLecturas` → Nueva columna):

```DAX
Tramo de llenado = IF ( FactLecturas[porcentaje] >= 90, "90-100", FORMAT ( INT ( FactLecturas[porcentaje] / 10 ) * 10, "00" ) & "-" & FORMAT ( INT ( FactLecturas[porcentaje] / 10 ) * 10 + 9, "00" ) )
```

Al terminar, comparen con los **valores de control** del final. Si `[Aperturas]` o `[Bloqueos por caneca llena]` no dan 3.643 y 209 con el filtro del período, revisen su fórmula: deben sumar solo los eventos de tipo `apertura` y `bloqueo_llena`, respectivamente.

## 3. Lo que falta: 5 visuales nuevos y 1 reutilizado

| # | Página | Cumple | Tipo de visual | Campos | Título |
|---|---|---|---|---|---|
| N1 | Uso y llenado | **Indicadores 1 a 4** | Tarjeta (nueva, el mismo tipo de su tarjeta de «Estado actual») | `[Llenado promedio %]`, `[% lecturas ≥ 90]`, `[Aperturas por día]`, `[Tasa de bloqueo %]` | Indicadores del período |
| N2 | Uso y llenado | **Univariado 1** | Columnas agrupadas | Eje X: `FactLecturas[Tramo de llenado]` · Eje Y: `[Lecturas]`; en el campo del eje Y: flecha → Mostrar valor como → Porcentaje del total general | Distribución del llenado (% de las lecturas por tramo) |
| N3 | Uso y llenado | **Bivariado 1** | Columnas agrupadas | Eje X: `DimCaneca[nombre]` · Eje Y: `[Llenado promedio %]`, `[Mediana de llenado %]`, `[% lecturas ≥ 90]` | Llenado por caneca: promedio, mediana y tiempo crítico (%) |
| N4 | Bloqueos y alarmas | **Univariado 2** | Barras agrupadas | Eje Y: `DimTipoEvento[tipo]` · Eje X: `FactEventos[cantidad]` (Suma), con etiquetas de datos | Eventos por tipo (cantidad) |
| N5 | Bloqueos y alarmas | **Multivariado** | Matriz | Filas: `DimCaneca[nombre]` y debajo `DimFecha[tipo_dia]` · Columnas: `DimHora[franja]` · Valores: `[Tasa de bloqueo %]`, `[Bloqueos por caneca llena]`, `[Aperturas]` · Formato → Elementos de celda → Color de fondo activado sobre `[Tasa de bloqueo %]` | Tasa de bloqueo por caneca, franja horaria y tipo de día (%) |
| R1 | Bloqueos y alarmas | **Bivariado 2** | Seleccionar el gráfico existente «Alarmas por día» y cambiarlo a **Gráfico de columnas agrupadas y de líneas** | Eje X: `DimFecha[nombre_dia]` · Eje Y (columnas): `[Bloqueos por caneca llena]` en lugar de `[Alarmas]` · Eje Y de línea: `[Tasa de bloqueo %]` | Bloqueos por día de la semana (cantidad y % de los intentos) |

- En la matriz N5, expandan las filas al segundo nivel (botón de dos flechas hacia abajo, arriba del visual) para ver las 24 combinaciones.
- Para que la franja salga en orden (Madrugada, Mañana, Tarde, Noche): en `DimHora` creen la columna `Orden franja = SWITCH ( DimHora[franja], "Madrugada", 1, "Mañana", 2, "Tarde", 3, "Noche", 4, 0 )` y ordenen `franja` por `Orden franja`.
- Las celdas de madrugada tienen muy pocos intentos: por eso la matriz muestra también bloqueos y aperturas.

## 4. Página «Estado actual»

- Subtítulo de la página: `Última lectura cargada en el data warehouse`.
- Agregar una tarjeta con `FactLecturas[fecha_hora]` (flecha del campo → Máximo), titulada «Fecha y hora de la última lectura». Con el ETL cada 5 minutos, esta fecha muestra qué tan al día está el informe.

## Valores de control (deben coincidir con el sitio)

Con el filtro del período simulado: llenado promedio 57,36 %; lecturas ≥ 90 %: 16,26 %; aperturas 3.643 (93,41 por día); bloqueos 209; tasa de bloqueo 5,43 %; alarmas 3 (14,77 h en promedio); domingo: 133 bloqueos y tasa de 30,16 %; C3 × Noche × Fin de semana: 49,45 %.

## Publicar e integrar en el sitio

1. Power BI Desktop → Inicio → **Publicar** → «Mi área de trabajo».
2. En app.powerbi.com abra el informe → **Archivo → Insertar informe → Publicar en la web (público)** → Crear código para insertar.
   - Si la opción no aparece o dice que el administrador la deshabilitó, la cuenta institucional no lo permite; habría que usar otra cuenta de Power BI.
   - El informe queda visible para cualquier persona con el enlace, sin iniciar sesión.
3. Copie el **vínculo** (empieza por `https://app.powerbi.com/view?r=`).
4. Péguelo en `docs/js/config.js`, entre las comillas de `POWERBI_URL`.
5. Publique: `git add docs/js/config.js`, `git commit -m "Integrar dashboard"`, `git push`.

## Actualización de los datos (tramo B)

### Informe publicado (el del iframe)

- El modelo está en **Importar**: los datos viven en el servicio de Power BI y cambian solo al actualizar el modelo. «Publicar en la web» guarda la vista en caché **una hora**.
- «Publicar en la web» **no admite DirectQuery**; el informe del sitio debe seguir en Importar.
- Para actualizarlo desde el SQL Server local:
  1. Descargar e instalar **On-premises data gateway (personal mode)** desde app.powerbi.com → icono de descarga → «Data Gateway». Iniciar sesión con la misma cuenta de Power BI.
  2. En el servicio: modelo semántico → Configuración → **Credenciales del origen de datos** → escribir usuario y contraseña de SQL Server.
  3. **Actualización programada** → activar y agregar las horas.
- **Límite:** en capacidad compartida (licencia gratuita o Pro), **8 actualizaciones programadas al día**. Tras dos meses sin uso, Power BI pausa la programación.
- **El computador debe estar encendido** y con la sesión iniciada a la hora de cada actualización: la puerta de enlace personal es una aplicación, no un servicio de Windows.
- Sin puerta de enlace, la alternativa es manual: «Actualizar» en Desktop y volver a **Publicar**.

### Demostración en vivo (Power BI Desktop)

- La **actualización automática de página** solo funciona con **DirectQuery**; el modelo actual (Importar) no la admite.
- Recomendación: un **informe pequeño aparte**, `Estado en vivo.pbix`, en DirectQuery, con una sola página. No mezclarlo con el informe principal, porque un informe con DirectQuery no se puede «Publicar en la web».
  1. Obtener datos → SQL Server → servidor `localhost\SQLEXPRESS`, base `VertederoDW` → modo **DirectQuery** → tablas `FactLecturas`, `DimCaneca`, `DimEstadoLlenado`.
  2. Medida: `Llenado actual % = VAR t = MAX ( FactLecturas[fecha_hora] ) RETURN CALCULATE ( AVERAGE ( FactLecturas[porcentaje] ), FactLecturas[fecha_hora] = t )`.
  3. Tres medidores (uno por caneca, con filtro de visual por `DimCaneca[nombre]`) y una tarjeta con `MAX(FactLecturas[fecha_hora])`.
  4. Clic en el lienzo → panel Formato → **Actualización de página** → Activar → cada 10 segundos.
- En Desktop no hay intervalo mínimo; en el servicio con capacidad compartida el mínimo es **30 minutos**. Úselo solo en Desktop.
- El ETL (tramo A) carga el data warehouse cada 5 minutos, así que este informe muestra lecturas con hasta 5 minutos de retraso. Si en la demostración se necesita ver cada lectura al instante, se puede apuntar el informe a la base `Vertedero` (tablas `Lecturas` y `Canecas`), que recibe las lecturas de la ESP32 cada 10 segundos.
