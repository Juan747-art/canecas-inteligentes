# Power BI: «Tablero Vertedero»

El tablero se rediseñó el 13 de noviembre de 2026 a partir del avance del equipo (versión del 7 de noviembre). El equipo lo aprobó.

## Archivos

| Ruta | Qué es |
|---|---|
| `powerbi/proyecto/Tablero Vertedero.pbip` | **Versión de trabajo** (proyecto de Power BI). El informe está en formato PBIR (JSON) y el modelo en TMDL, en las carpetas `Tablero Vertedero.Report` y `Tablero Vertedero.SemanticModel`. Se abre con Power BI Desktop. |
| `powerbi/tema_canecas.json` | Tema visual: colores de las canecas (C1 gris azulado por «blanca», C2 carbón, C3 verde), verde del sitio como acento, tarjetas blancas sobre fondo gris claro, Segoe UI. |
| `powerbi/respaldo/` (no se sube) | Versión original del 7 de noviembre (`.pbix` y proyecto). |
| `Tablero Vertedero.pbix` (no se sube) | Copia para publicar: se guarda desde el `.pbip` con File → Save as. |

La caché de datos del proyecto (`.pbi/cache.abf`) no se sube al repositorio.

## Páginas

Lienzo de 1280 × 720. Las páginas de análisis tienen un filtro de página para el **período simulado** (27/09/2026 a 04/11/2026) y segmentaciones de caneca y tipo de día.

| Página | Visuales | Requisito de la guía |
|---|---|---|
| **Estado actual** (sin filtro de período) | 3 medidores de `[Llenado actual %]`, uno por caneca, con el color de la caneca y el umbral de 90 %; filtro desplegable «Día» (solo muestra los días con lecturas, el más reciente primero); tarjeta «Última lectura cargada» con las lecturas recibidas; tarjeta de calidad y alarmas (lecturas válidas, alarmas, horas en alarma, peso simulado actual); nota de lectura. | Estado en vivo |
| **Uso y llenado** | Tarjeta con llenado promedio, lecturas ≥ 90 %, aperturas por día y lecturas analizadas. Llenado promedio por hora y caneca. Distribución del llenado por tramo. Llenado promedio por día y caneca. Aperturas por hora. Llenado por caneca (promedio, mediana, ≥ 90 %). Matriz de aperturas por día y franja. | Indicadores 1 a 3 · **Bivariado 3** · **Univariado 1** · tendencia · **Univariado 3** · **Bivariado 1** · apoyo de la decisión 2 |
| **Bloqueos y alarmas** | Tarjeta con bloqueos, tasa de bloqueo, alarmas y duración promedio. Combinado de bloqueos (columnas) y tasa de bloqueo (línea) por día de la semana. Matriz de tasa de bloqueo por caneca × tipo de día × franja (también bloqueos y aperturas). Eventos por tipo. Bloqueos por caneca. Tabla de alarmas. | Indicadores 4 y 5 · **Bivariado 2** · **Multivariado** · **Univariado 2** · apoyo · apoyo del indicador 5 |
| **Más detalle** | Anillo de lecturas por estado (verde con espacio, ámbar casi llena, rojo llena). Dispersión llenado–peso simulado. Peso simulado máximo por día. Gramos por punto de llenado. | Apoyo (el peso es simulado) |

## Cambios en el modelo

- **Formato** en las medidas que no lo tenían: porcentajes 0–100 con 2 decimales y razones como `0.00%`.
- **Medidas nuevas** en `Medidas`:

```DAX
% lecturas ≥ 90 = DIVIDE ( CALCULATE ( [Lecturas], FactLecturas[porcentaje] >= 90 ), [Lecturas] ) * 100
Mediana de llenado % = MEDIAN ( FactLecturas[porcentaje] )
Aperturas por día = DIVIDE ( [Aperturas], DISTINCTCOUNT ( FactLecturas[fecha_key] ) )
Horas promedio de alarma = DIVIDE ( SUM ( FactAlarmas[duracion_min] ), 60 * [Alarmas] )
Eventos = SUM ( FactEventos[cantidad] )
% de las lecturas = DIVIDE ( [Lecturas], CALCULATE ( [Lecturas], ALLSELECTED ( FactLecturas[Tramo de llenado] ) ) )
Última lectura = MAX ( FactLecturas[fecha_hora] )
```

- **Columnas calculadas**: `DimFecha[Tipo de día]` («Laborable» o «Fin de semana», a partir de `es_fin_de_semana`); `FactLecturas[Tramo de llenado]` (00-09 … 80-89, 90-100); `DimHora[Orden franja]` (oculta, calculada desde `hora_key`) para ordenar la franja como Madrugada, Mañana, Tarde y Noche. `hora_texto` se ordena por `hora_key`.
- La tasa de bloqueo es la medida existente `[% intentos bloqueados]` = bloqueos ÷ (aperturas + bloqueos).
- **Corrección del 13 de noviembre de 2026:** la relación `FactEventos.hora_key → DimHora` estaba **inactiva**, así que la hora y la franja no filtraban los eventos (las gráficas de aperturas por hora, aperturas por día y franja y la matriz multivariada repetían el total en cada hora o franja). Se activó. También se desactivó la fecha y hora automática (se quitaron las tablas ocultas `LocalDateTable_*` y `DateTableTemplate_*`, que ningún visual usaba). Respaldo del modelo anterior en `powerbi/respaldo/` (no se sube).

## Para cambiar el diseño

Con Power BI Desktop **cerrado**, se editan los archivos de `powerbi/proyecto`; al abrir el `.pbip` se ven los cambios. Con Desktop abierto, la opción «Detect and reload external PBIP changes» los recarga. Después de cualquier cambio hecho en Desktop, guarden el proyecto (File → Save) para que los archivos queden al día.

## Valores de control (deben coincidir con el sitio)

Con el filtro del período simulado: llenado promedio 57,36 %; lecturas ≥ 90 %: 16,26 %; aperturas 3.643 (93,41 por día); bloqueos 209; tasa de bloqueo 5,43 %; alarmas 3 (14,77 h en promedio); domingo: 133 bloqueos y tasa de 30,16 %; C3 × Noche × Fin de semana: 49,45 %. Aperturas por franja: Madrugada 39, Mañana 1.380, Tarde 1.437, Noche 787; bloqueos por franja: 9, 0, 64 y 136. Aperturas a las 12 h: 509.

El formato de los números en la vista pública sigue el idioma del navegador de quien la abre (en español: 5,43 %); en Power BI Desktop depende de Archivo → Opciones → Archivo actual → Configuración regional.

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
