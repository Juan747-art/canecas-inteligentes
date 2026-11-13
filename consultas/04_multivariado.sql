/* =====================================================================
   04_multivariado.sql
   Analisis multivariado del periodo simulado
   (2026-09-27 a 2026-11-04, fecha_key 20260927-20261104).

   Combina TRES variables en una sola consulta:
     caneca (C1, C2, C3) x franja horaria (4) x tipo de dia (2) = 24 celdas
   Para cada celda calcula el llenado, el uso y los bloqueos.
   La combinacion se calcula directamente; no se deduce de tres
   resultados separados.
   ===================================================================== */
USE VertederoDW;
SET NOCOUNT ON;
DECLARE @desde INT = 20260927, @hasta INT = 20261104;

WITH lec AS (
  SELECT c.nombre AS caneca, h.franja, f.tipo_dia,
         COUNT(*) AS lecturas,
         COUNT(DISTINCT l.fecha_key) AS dias,
         AVG(1.0 * l.porcentaje) AS llenado_promedio,
         SUM(CASE WHEN l.porcentaje >= 90 THEN 1 ELSE 0 END) AS lecturas_90
  FROM dbo.FactLecturas l
  JOIN dbo.DimCaneca c ON c.caneca_key = l.caneca_key
  JOIN dbo.DimHora h   ON h.hora_key = l.hora_key
  JOIN dbo.DimFecha f  ON f.fecha_key = l.fecha_key
  WHERE l.fecha_key BETWEEN @desde AND @hasta
  GROUP BY c.nombre, h.franja, f.tipo_dia),
ev AS (
  SELECT c.nombre AS caneca, h.franja, f.tipo_dia,
         SUM(CASE WHEN t.tipo = N'apertura' THEN 1 ELSE 0 END) AS aperturas,
         SUM(CASE WHEN t.tipo = N'bloqueo_llena' THEN 1 ELSE 0 END) AS bloqueos
  FROM dbo.FactEventos e
  JOIN dbo.DimTipoEvento t ON t.tipo_evento_key = e.tipo_evento_key
  JOIN dbo.DimCaneca c ON c.caneca_key = e.caneca_key
  JOIN dbo.DimHora h   ON h.hora_key = e.hora_key
  JOIN dbo.DimFecha f  ON f.fecha_key = e.fecha_key
  WHERE e.fecha_key BETWEEN @desde AND @hasta
  GROUP BY c.nombre, h.franja, f.tipo_dia)
SELECT lec.caneca, lec.franja, lec.tipo_dia,
       lec.dias, lec.lecturas,
       CAST(lec.llenado_promedio AS DECIMAL(6,2)) AS llenado_promedio_pct,
       CAST(100.0 * lec.lecturas_90 / lec.lecturas AS DECIMAL(6,2)) AS pct_lecturas_90_o_mas,
       ISNULL(ev.aperturas, 0) AS aperturas,
       CAST(1.0 * ISNULL(ev.aperturas, 0) / lec.dias AS DECIMAL(8,2)) AS aperturas_por_dia,
       ISNULL(ev.bloqueos, 0) AS bloqueos,
       CAST(1.0 * ISNULL(ev.bloqueos, 0) / lec.dias AS DECIMAL(8,2)) AS bloqueos_por_dia,
       CAST(100.0 * ISNULL(ev.bloqueos, 0) / NULLIF(ISNULL(ev.aperturas, 0) + ISNULL(ev.bloqueos, 0), 0) AS DECIMAL(6,2)) AS tasa_bloqueo_pct
FROM lec
LEFT JOIN ev ON ev.caneca = lec.caneca AND ev.franja = lec.franja AND ev.tipo_dia = lec.tipo_dia
ORDER BY lec.caneca,
         CASE lec.franja WHEN N'Madrugada' THEN 1 WHEN N'Mañana' THEN 2 WHEN N'Tarde' THEN 3 ELSE 4 END,
         lec.tipo_dia DESC;
