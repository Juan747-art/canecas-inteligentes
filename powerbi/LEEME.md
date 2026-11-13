# Power BI: visuales por crear o ajustar y actualización de los datos

El archivo `Tablero Vertedero.pbix` tiene hoy tres páginas («Estado actual», «Page 1» y «Page 2») y una tabla `Medidas`. Esta lista indica qué crear o ajustar para que el dashboard cumpla el punto 3 de la guía y coincida con los análisis del sitio.

## Antes de empezar

- **Filtro de período.** En cada página de análisis, en el panel Filtros → «Filtros de esta página», arrastre `DimFecha[fecha]` y deje «está entre 27/09/2026 y 04/11/2026». Así los valores coinciden con el sitio (período simulado).
- **Subtítulo de todos los visuales de análisis:** `Período simulado: 27 sep – 4 nov 2026`.
- **Renombrar páginas:** «Page 1» → `Uso y llenado`; «Page 2» → `Bloqueos y alarmas`.
- **Medidas nuevas** (Inicio → Nueva medida, en la tabla `Medidas`):

```DAX
Bloqueos = CALCULATE ( SUM ( FactEventos[cantidad] ), DimTipoEvento[tipo] = "bloqueo_llena" )
Intentos = CALCULATE ( SUM ( FactEventos[cantidad] ), DimTipoEvento[tipo] IN { "apertura", "bloqueo_llena" } )
Tasa de bloqueo % = DIVIDE ( [Bloqueos], [Intentos] ) * 100
Días con datos = DISTINCTCOUNT ( FactLecturas[fecha_key] )
Aperturas por día = DIVIDE ( [Aperturas], [Días con datos] )
% lecturas ≥ 90 = DIVIDE ( CALCULATE ( COUNTROWS ( FactLecturas ), FactLecturas[porcentaje] >= 90 ), COUNTROWS ( FactLecturas ) ) * 100
Mediana de llenado % = MEDIAN ( FactLecturas[porcentaje] )
Horas promedio de alarma = DIVIDE ( SUM ( FactAlarmas[duracion_min] ), 60 * COUNTROWS ( FactAlarmas ) )
```

Si ya existe `Bloqueos por caneca llena`, puede usarla en lugar de `Bloqueos`. Compruebe que `[Aperturas]` cuenta solo eventos de tipo `apertura`.

- **Columna nueva** en `FactLecturas` (para el histograma):

```DAX
Tramo de llenado = IF ( FactLecturas[porcentaje] >= 90, "90-100", FORMAT ( INT ( FactLecturas[porcentaje] / 10 ) * 10, "00" ) & "-" & FORMAT ( INT ( FactLecturas[porcentaje] / 10 ) * 10 + 9, "00" ) )
```

## Página «Uso y llenado»

| # | Cumple | Tipo de visual | Campos | Título |
|---|---|---|---|---|
| 1 | Indicador 1 | Tarjeta | `[Llenado promedio %]` | Llenado promedio (%) |
| 2 | Indicador 2 | Tarjeta | `[% lecturas ≥ 90]` | Lecturas en estado crítico, ≥ 90 % (% de las lecturas) |
| 3 | Indicador 3 | Tarjeta | `[Aperturas por día]` | Aperturas de tapa por día |
| 4 | Indicador 4 | Tarjeta | `[Tasa de bloqueo %]` | Tasa de bloqueo (% de los intentos) |
| 5 | Indicador 5 | Tarjeta (2 campos) | `[Alarmas]`, `[Horas promedio de alarma]` | Alarmas conjuntas y duración promedio (h) |
| 6 | Univariado 1 | Gráfico de columnas agrupadas | Eje X: `FactLecturas[Tramo de llenado]` · Eje Y: `[Lecturas]` mostrado como «% del total general» | Distribución del llenado (% de las lecturas por tramo) |
| 7 | Univariado 3 | Columnas agrupadas (**ajustar** el existente: quitar `DimCaneca[nombre]` de Leyenda) | Eje X: `DimHora[hora_texto]` · Eje Y: `[Aperturas]` | Aperturas por hora del día (cantidad) |
| 8 | Bivariado 3 | Gráfico de líneas (**ya existe**: «Llenado promedio por hora») | Eje X: `DimHora[hora_texto]` · Leyenda: `DimCaneca[nombre]` · Eje Y: `[Llenado promedio %]` | Llenado promedio por hora y caneca (%) |
| 9 | Bivariado 1 | Columnas agrupadas | Eje X: `DimCaneca[nombre]` · Eje Y: `[Llenado promedio %]`, `[Mediana de llenado %]`, `[% lecturas ≥ 90]` | Llenado por caneca: promedio, mediana y tiempo crítico (%) |
| 10 | Filtros | Segmentaciones (**ya existen**) | `DimCaneca[nombre]`; `DimFecha[tipo_dia]` (nueva) | — |

Ordene `hora_texto` por `hora_key` (Herramientas de columnas → Ordenar por columna).

## Página «Bloqueos y alarmas»

| # | Cumple | Tipo de visual | Campos | Título |
|---|---|---|---|---|
| 11 | Univariado 2 | Gráfico de barras agrupadas | Eje Y: `DimTipoEvento[tipo]` · Eje X: `SUM(FactEventos[cantidad])` con etiquetas de datos | Eventos por tipo (cantidad) |
| 12 | Bivariado 2 | Columnas agrupadas y de líneas | Eje X: `DimFecha[nombre_dia]` (ordenado por `dia_semana`) · Columnas: `[Bloqueos]` · Línea: `[Tasa de bloqueo %]` | Bloqueos por día de la semana (cantidad y % de los intentos) |
| 13 | **Multivariado** | Matriz | Filas: `DimCaneca[nombre]`, luego `DimFecha[tipo_dia]` · Columnas: `DimHora[franja]` (ordenada: Madrugada, Mañana, Tarde, Noche) · Valores: `[Tasa de bloqueo %]`, `[Bloqueos]`, `[Aperturas]` · Formato condicional de fondo sobre `[Tasa de bloqueo %]` | Tasa de bloqueo por caneca, franja horaria y tipo de día (%) |
| 14 | Apoyo | Tabla (**ajustar** la existente) | `FactAlarmas[fecha_inicio]`, `[fecha_fin]` (como fecha y hora, sin jerarquía), `duracion_min`, `pct_c1`, `pct_c2`, `pct_c3` (sin resumir) | Alarmas conjuntas: inicio, fin, duración (min) y llenado (%) |
| 15 | Apoyo | Anillo (**ya existe**) | `DimEstadoLlenado[estado]`, `[Lecturas]` | Lecturas por estado de llenado (% de las lecturas) |

En la matriz (13), expanda las filas hasta el segundo nivel para que se vean las 24 combinaciones. Las celdas de madrugada tienen muy pocos intentos: por eso se muestran también `[Bloqueos]` y `[Aperturas]`.

## Página «Estado actual»

- Póngale el subtítulo `Última lectura cargada en el data warehouse` y agregue una tarjeta con `MAX(FactLecturas[fecha_hora])` titulada «Fecha y hora de la última lectura».
- Corrija los títulos de los medidores (`C3 · Orgánicos`, sin punto final).
- Esta página **no** debe llevar el filtro del período simulado.
- Los gráficos de peso de «Page 2» (dispersión llenado-peso, gramos por punto, peso máximo) muestran una variable simulada y calculada a partir del llenado. Si los conserva, titule «Peso simulado (g)»; no aportan a los conocimientos del sitio.

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
