/* =====================================================================
   03_bivariados.sql
   Tres analisis bivariados del periodo simulado
   (2026-09-27 a 2026-11-04, fecha_key 20260927-20261104).
   Las relaciones se leen como asociaciones, no como causas.
   ===================================================================== */
USE VertederoDW;
SET NOCOUNT ON;
DECLARE @desde INT = 20260927, @hasta INT = 20261104;

PRINT '== B1. Caneca x llenado (categorica + numerica) ==';
SELECT DISTINCT c.nombre AS caneca, c.tipo_residuo,
       COUNT(*) OVER (PARTITION BY c.nombre, c.tipo_residuo) AS lecturas,
       CAST(AVG(1.0 * l.porcentaje) OVER (PARTITION BY c.nombre, c.tipo_residuo) AS DECIMAL(6,2)) AS promedio_pct,
       CAST(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY l.porcentaje) OVER (PARTITION BY c.nombre, c.tipo_residuo) AS DECIMAL(6,2)) AS mediana_pct,
       CAST(STDEV(1.0 * l.porcentaje) OVER (PARTITION BY c.nombre, c.tipo_residuo) AS DECIMAL(6,2)) AS desviacion_pct,
       MAX(l.porcentaje) OVER (PARTITION BY c.nombre, c.tipo_residuo) AS maximo_pct,
       CAST(100.0 * SUM(CASE WHEN l.porcentaje >= 90 THEN 1 ELSE 0 END) OVER (PARTITION BY c.nombre, c.tipo_residuo)
            / COUNT(*) OVER (PARTITION BY c.nombre, c.tipo_residuo) AS DECIMAL(6,2)) AS pct_lecturas_90_o_mas
FROM dbo.FactLecturas l JOIN dbo.DimCaneca c ON c.caneca_key = l.caneca_key
WHERE l.fecha_key BETWEEN @desde AND @hasta
ORDER BY 1;

PRINT '== B2. Dia de la semana x uso y bloqueos (categorica + numerica) ==';
PRINT '-- B2.a por dia de la semana';
WITH dias AS (
  SELECT f.dia_semana, f.nombre_dia, f.tipo_dia, COUNT(DISTINCT l.fecha_key) AS dias
  FROM dbo.FactLecturas l JOIN dbo.DimFecha f ON f.fecha_key = l.fecha_key
  WHERE l.fecha_key BETWEEN @desde AND @hasta
  GROUP BY f.dia_semana, f.nombre_dia, f.tipo_dia),
ev AS (
  SELECT f.dia_semana,
         SUM(CASE WHEN t.tipo = N'apertura' THEN 1 ELSE 0 END) AS aperturas,
         SUM(CASE WHEN t.tipo = N'bloqueo_llena' THEN 1 ELSE 0 END) AS bloqueos
  FROM dbo.FactEventos e
  JOIN dbo.DimTipoEvento t ON t.tipo_evento_key = e.tipo_evento_key
  JOIN dbo.DimFecha f ON f.fecha_key = e.fecha_key
  WHERE e.fecha_key BETWEEN @desde AND @hasta
  GROUP BY f.dia_semana)
SELECT d.dia_semana, d.nombre_dia, d.tipo_dia, d.dias,
       ev.aperturas, CAST(1.0 * ev.aperturas / d.dias AS DECIMAL(8,2)) AS aperturas_por_dia,
       ev.bloqueos,  CAST(1.0 * ev.bloqueos / d.dias AS DECIMAL(8,2)) AS bloqueos_por_dia,
       CAST(100.0 * ev.bloqueos / SUM(ev.bloqueos) OVER () AS DECIMAL(6,2)) AS pct_de_los_bloqueos,
       CAST(100.0 * ev.bloqueos / NULLIF(ev.aperturas + ev.bloqueos, 0) AS DECIMAL(6,2)) AS tasa_bloqueo_pct
FROM dias d JOIN ev ON ev.dia_semana = d.dia_semana
ORDER BY d.dia_semana;

PRINT '-- B2.b por tipo de dia (laborable / fin de semana)';
WITH dias AS (
  SELECT f.tipo_dia, COUNT(DISTINCT l.fecha_key) AS dias
  FROM dbo.FactLecturas l JOIN dbo.DimFecha f ON f.fecha_key = l.fecha_key
  WHERE l.fecha_key BETWEEN @desde AND @hasta
  GROUP BY f.tipo_dia),
ev AS (
  SELECT f.tipo_dia,
         SUM(CASE WHEN t.tipo = N'apertura' THEN 1 ELSE 0 END) AS aperturas,
         SUM(CASE WHEN t.tipo = N'bloqueo_llena' THEN 1 ELSE 0 END) AS bloqueos
  FROM dbo.FactEventos e
  JOIN dbo.DimTipoEvento t ON t.tipo_evento_key = e.tipo_evento_key
  JOIN dbo.DimFecha f ON f.fecha_key = e.fecha_key
  WHERE e.fecha_key BETWEEN @desde AND @hasta
  GROUP BY f.tipo_dia)
SELECT d.tipo_dia, d.dias, ev.aperturas,
       CAST(1.0 * ev.aperturas / d.dias AS DECIMAL(8,2)) AS aperturas_por_dia,
       ev.bloqueos, CAST(1.0 * ev.bloqueos / d.dias AS DECIMAL(8,2)) AS bloqueos_por_dia,
       CAST(100.0 * ev.bloqueos / NULLIF(ev.aperturas + ev.bloqueos, 0) AS DECIMAL(6,2)) AS tasa_bloqueo_pct
FROM dias d JOIN ev ON ev.tipo_dia = d.tipo_dia
ORDER BY d.tipo_dia DESC;

PRINT '-- B2.c llenado promedio por dia de la semana (apoyo)';
SELECT f.dia_semana, f.nombre_dia,
       CAST(AVG(1.0 * l.porcentaje) AS DECIMAL(6,2)) AS llenado_promedio_pct,
       CAST(100.0 * SUM(CASE WHEN l.porcentaje >= 90 THEN 1 ELSE 0 END) / COUNT(*) AS DECIMAL(6,2)) AS pct_lecturas_90_o_mas
FROM dbo.FactLecturas l JOIN dbo.DimFecha f ON f.fecha_key = l.fecha_key
WHERE l.fecha_key BETWEEN @desde AND @hasta
GROUP BY f.dia_semana, f.nombre_dia ORDER BY f.dia_semana;

PRINT '== B3. Hora del dia x llenado promedio (numerica + numerica) ==';
SELECT h.hora_key AS hora, h.franja, COUNT(*) AS lecturas,
       CAST(AVG(1.0 * l.porcentaje) AS DECIMAL(6,2)) AS llenado_promedio_pct,
       CAST(AVG(CASE WHEN c.id_caneca = 1 THEN 1.0 * l.porcentaje END) AS DECIMAL(6,2)) AS c1_pct,
       CAST(AVG(CASE WHEN c.id_caneca = 2 THEN 1.0 * l.porcentaje END) AS DECIMAL(6,2)) AS c2_pct,
       CAST(AVG(CASE WHEN c.id_caneca = 3 THEN 1.0 * l.porcentaje END) AS DECIMAL(6,2)) AS c3_pct
FROM dbo.FactLecturas l
JOIN dbo.DimHora h ON h.hora_key = l.hora_key
JOIN dbo.DimCaneca c ON c.caneca_key = l.caneca_key
WHERE l.fecha_key BETWEEN @desde AND @hasta
GROUP BY h.hora_key, h.franja
ORDER BY h.hora_key;

PRINT '-- B3.b la misma curva separando domingo (sin recoleccion) del resto';
SELECT h.hora_key AS hora,
       CAST(AVG(CASE WHEN f.dia_semana <> 7 THEN 1.0 * l.porcentaje END) AS DECIMAL(6,2)) AS lunes_a_sabado_pct,
       CAST(AVG(CASE WHEN f.dia_semana = 7 THEN 1.0 * l.porcentaje END) AS DECIMAL(6,2)) AS domingo_pct
FROM dbo.FactLecturas l
JOIN dbo.DimHora h ON h.hora_key = l.hora_key
JOIN dbo.DimFecha f ON f.fecha_key = l.fecha_key
WHERE l.fecha_key BETWEEN @desde AND @hasta
GROUP BY h.hora_key
ORDER BY h.hora_key;
