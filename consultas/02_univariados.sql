/* =====================================================================
   02_univariados.sql
   Tres analisis univariados del periodo simulado
   (2026-09-27 a 2026-11-04, fecha_key 20260927-20261104).
   ===================================================================== */
USE VertederoDW;
SET NOCOUNT ON;
DECLARE @desde INT = 20260927, @hasta INT = 20261104;

PRINT '== U1. Distribucion del porcentaje de llenado (variable numerica) ==';
PRINT '-- U1.a medidas de resumen';
SELECT DISTINCT
       COUNT(*) OVER () AS lecturas,
       CAST(AVG(1.0 * l.porcentaje) OVER () AS DECIMAL(6,2)) AS promedio,
       CAST(PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY l.porcentaje) OVER () AS DECIMAL(6,2)) AS q1,
       CAST(PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY l.porcentaje) OVER () AS DECIMAL(6,2)) AS mediana,
       CAST(PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY l.porcentaje) OVER () AS DECIMAL(6,2)) AS q3,
       CAST(STDEV(1.0 * l.porcentaje) OVER () AS DECIMAL(6,2)) AS desviacion_estandar,
       MIN(l.porcentaje) OVER () AS minimo,
       MAX(l.porcentaje) OVER () AS maximo
FROM dbo.FactLecturas l
WHERE l.fecha_key BETWEEN @desde AND @hasta;

PRINT '-- U1.b histograma en tramos de 10 puntos';
SELECT CASE WHEN l.porcentaje >= 90 THEN '90-100'
            ELSE CONCAT(RIGHT('0' + CAST(l.porcentaje / 10 * 10 AS VARCHAR(2)), 2), '-', RIGHT('0' + CAST(l.porcentaje / 10 * 10 + 9 AS VARCHAR(2)), 2)) END AS tramo_pct,
       COUNT(*) AS lecturas,
       CAST(100.0 * COUNT(*) / SUM(COUNT(*)) OVER () AS DECIMAL(6,2)) AS pct_del_total
FROM dbo.FactLecturas l
WHERE l.fecha_key BETWEEN @desde AND @hasta
GROUP BY CASE WHEN l.porcentaje >= 90 THEN '90-100'
              ELSE CONCAT(RIGHT('0' + CAST(l.porcentaje / 10 * 10 AS VARCHAR(2)), 2), '-', RIGHT('0' + CAST(l.porcentaje / 10 * 10 + 9 AS VARCHAR(2)), 2)) END
ORDER BY 1;

PRINT '-- U1.c lecturas por estado de llenado (DimEstadoLlenado)';
SELECT s.estado, s.desde_pct, s.hasta_pct, COUNT(*) AS lecturas,
       CAST(100.0 * COUNT(*) / SUM(COUNT(*)) OVER () AS DECIMAL(6,2)) AS pct_del_total
FROM dbo.FactLecturas l JOIN dbo.DimEstadoLlenado s ON s.estado_key = l.estado_key
WHERE l.fecha_key BETWEEN @desde AND @hasta
GROUP BY s.estado_key, s.estado, s.desde_pct, s.hasta_pct
ORDER BY s.estado_key;

PRINT '== U2. Distribucion de los eventos por tipo (variable categorica) ==';
SELECT t.tipo, t.grupo, COUNT(*) AS eventos,
       CAST(100.0 * COUNT(*) / SUM(COUNT(*)) OVER () AS DECIMAL(6,2)) AS pct_del_total
FROM dbo.FactEventos e JOIN dbo.DimTipoEvento t ON t.tipo_evento_key = e.tipo_evento_key
WHERE e.fecha_key BETWEEN @desde AND @hasta
GROUP BY t.tipo, t.grupo
ORDER BY eventos DESC;

PRINT '== U3. Distribucion de las aperturas por hora del dia (variable temporal) ==';
SELECT h.hora_key AS hora, h.hora_texto, h.franja, COUNT(e.evento_key) AS aperturas,
       CAST(100.0 * COUNT(e.evento_key) / SUM(COUNT(e.evento_key)) OVER () AS DECIMAL(6,2)) AS pct_del_total
FROM dbo.DimHora h
LEFT JOIN (dbo.FactEventos e JOIN dbo.DimTipoEvento t ON t.tipo_evento_key = e.tipo_evento_key AND t.tipo = N'apertura')
       ON e.hora_key = h.hora_key AND e.fecha_key BETWEEN @desde AND @hasta
WHERE h.hora_key <> -1
GROUP BY h.hora_key, h.hora_texto, h.franja
ORDER BY h.hora_key;

PRINT '-- U3.b concentracion en los tres picos (06-08 h, 11-13 h, 17-19 h)';
SELECT CASE WHEN e.hora_key BETWEEN 6 AND 8 THEN '1. Manana 06-08 h'
            WHEN e.hora_key BETWEEN 11 AND 13 THEN '2. Almuerzo 11-13 h'
            WHEN e.hora_key BETWEEN 17 AND 19 THEN '3. Tarde 17-19 h'
            ELSE '4. Resto (15 horas)' END AS bloque,
       COUNT(*) AS aperturas,
       CAST(100.0 * COUNT(*) / SUM(COUNT(*)) OVER () AS DECIMAL(6,2)) AS pct_del_total
FROM dbo.FactEventos e JOIN dbo.DimTipoEvento t ON t.tipo_evento_key = e.tipo_evento_key
WHERE e.fecha_key BETWEEN @desde AND @hasta AND t.tipo = N'apertura'
GROUP BY CASE WHEN e.hora_key BETWEEN 6 AND 8 THEN '1. Manana 06-08 h'
              WHEN e.hora_key BETWEEN 11 AND 13 THEN '2. Almuerzo 11-13 h'
              WHEN e.hora_key BETWEEN 17 AND 19 THEN '3. Tarde 17-19 h'
              ELSE '4. Resto (15 horas)' END
ORDER BY 1;
