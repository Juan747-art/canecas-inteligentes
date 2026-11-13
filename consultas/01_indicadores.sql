/* =====================================================================
   01_indicadores.sql
   Cinco indicadores generales del periodo simulado
   (2026-09-27 a 2026-11-04, fecha_key 20260927-20261104).
   ===================================================================== */
USE VertederoDW;
SET NOCOUNT ON;
DECLARE @desde INT = 20260927, @hasta INT = 20261104;

PRINT '== I1. Llenado promedio (%) general y por caneca ==';
SELECT ISNULL(c.nombre, 'TODAS') AS caneca,
       COUNT(*) AS lecturas,
       CAST(AVG(1.0 * l.porcentaje) AS DECIMAL(6,2)) AS llenado_promedio_pct
FROM dbo.FactLecturas l JOIN dbo.DimCaneca c ON c.caneca_key = l.caneca_key
WHERE l.fecha_key BETWEEN @desde AND @hasta
GROUP BY ROLLUP(c.nombre)
ORDER BY GROUPING(c.nombre) DESC, c.nombre;

PRINT '== I2. Porcentaje de lecturas en estado critico (>= 90 %) y llenas (>= 95 %) ==';
SELECT ISNULL(c.nombre, 'TODAS') AS caneca,
       COUNT(*) AS lecturas,
       SUM(CASE WHEN l.porcentaje >= 90 THEN 1 ELSE 0 END) AS lecturas_90_o_mas,
       CAST(100.0 * SUM(CASE WHEN l.porcentaje >= 90 THEN 1 ELSE 0 END) / COUNT(*) AS DECIMAL(6,2)) AS pct_lecturas_90_o_mas,
       SUM(CASE WHEN l.porcentaje >= 95 THEN 1 ELSE 0 END) AS lecturas_95_o_mas,
       CAST(100.0 * SUM(CASE WHEN l.porcentaje >= 95 THEN 1 ELSE 0 END) / COUNT(*) AS DECIMAL(6,2)) AS pct_lecturas_95_o_mas
FROM dbo.FactLecturas l JOIN dbo.DimCaneca c ON c.caneca_key = l.caneca_key
WHERE l.fecha_key BETWEEN @desde AND @hasta
GROUP BY ROLLUP(c.nombre)
ORDER BY GROUPING(c.nombre) DESC, c.nombre;

PRINT '== I3. Aperturas de tapa: total y promedio por dia ==';
SELECT ISNULL(c.nombre, 'TODAS') AS caneca,
       COUNT(*) AS aperturas,
       (SELECT COUNT(DISTINCT fecha_key) FROM dbo.FactLecturas WHERE fecha_key BETWEEN @desde AND @hasta) AS dias,
       CAST(1.0 * COUNT(*) / (SELECT COUNT(DISTINCT fecha_key) FROM dbo.FactLecturas WHERE fecha_key BETWEEN @desde AND @hasta) AS DECIMAL(8,2)) AS aperturas_por_dia
FROM dbo.FactEventos e
JOIN dbo.DimTipoEvento t ON t.tipo_evento_key = e.tipo_evento_key
JOIN dbo.DimCaneca c ON c.caneca_key = e.caneca_key
WHERE e.fecha_key BETWEEN @desde AND @hasta AND t.tipo = N'apertura'
GROUP BY ROLLUP(c.nombre)
ORDER BY GROUPING(c.nombre) DESC, c.nombre;

PRINT '== I4. Tasa de bloqueo = bloqueos / (aperturas + bloqueos) ==';
SELECT ISNULL(c.nombre, 'TODAS') AS caneca,
       SUM(CASE WHEN t.tipo = N'apertura' THEN 1 ELSE 0 END) AS aperturas,
       SUM(CASE WHEN t.tipo = N'bloqueo_llena' THEN 1 ELSE 0 END) AS bloqueos,
       SUM(CASE WHEN t.tipo IN (N'apertura', N'bloqueo_llena') THEN 1 ELSE 0 END) AS intentos,
       CAST(100.0 * SUM(CASE WHEN t.tipo = N'bloqueo_llena' THEN 1 ELSE 0 END)
            / NULLIF(SUM(CASE WHEN t.tipo IN (N'apertura', N'bloqueo_llena') THEN 1 ELSE 0 END), 0) AS DECIMAL(6,2)) AS tasa_bloqueo_pct
FROM dbo.FactEventos e
JOIN dbo.DimTipoEvento t ON t.tipo_evento_key = e.tipo_evento_key
JOIN dbo.DimCaneca c ON c.caneca_key = e.caneca_key
WHERE e.fecha_key BETWEEN @desde AND @hasta
GROUP BY ROLLUP(c.nombre)
ORDER BY GROUPING(c.nombre) DESC, c.nombre;

PRINT '== I5. Alarmas conjuntas (las tres canecas sobre 90 %): numero y duracion ==';
SELECT COUNT(*) AS alarmas,
       SUM(a.duracion_min) AS minutos_totales,
       CAST(SUM(a.duracion_min) / 60.0 AS DECIMAL(8,2)) AS horas_totales,
       CAST(AVG(1.0 * a.duracion_min) / 60.0 AS DECIMAL(8,2)) AS horas_promedio,
       CAST(MIN(a.duracion_min) / 60.0 AS DECIMAL(8,2)) AS horas_min,
       CAST(MAX(a.duracion_min) / 60.0 AS DECIMAL(8,2)) AS horas_max
FROM dbo.FactAlarmas a
WHERE a.fecha_key BETWEEN @desde AND @hasta;

PRINT '-- I5 detalle de cada alarma';
SELECT a.id_alarma_origen AS alarma, f.nombre_dia AS dia_inicio, a.fecha_inicio, a.fecha_fin,
       a.duracion_min, CAST(a.duracion_min / 60.0 AS DECIMAL(6,2)) AS horas,
       a.pct_c1, a.pct_c2, a.pct_c3, a.rango_duracion
FROM dbo.FactAlarmas a JOIN dbo.DimFecha f ON f.fecha_key = a.fecha_key
WHERE a.fecha_key BETWEEN @desde AND @hasta
ORDER BY a.fecha_inicio;
