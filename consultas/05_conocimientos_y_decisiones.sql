/* =====================================================================
   05_conocimientos_y_decisiones.sql
   Comprobaciones adicionales que sustentan los cinco conocimientos y
   las dos decisiones (periodo simulado, fecha_key 20260927-20261104).

   Los valores principales de cada conocimiento salen de:
     K1 ciclo diario ................ 03_bivariados.sql  (B3 y B3.b)
     K2 diferencia entre canecas .... 03_bivariados.sql  (B1) y 01 (I2, I4)
     K3 tres picos de uso ........... 02_univariados.sql (U3 y U3.b)
     K4 domingos y bloqueos ......... 03_bivariados.sql  (B2.a) y 01 (I5)
     K5 combinacion de 3 variables .. 04_multivariado.sql
   Aqui se revisa que esos hallazgos no dependan de un solo dia atipico.
   ===================================================================== */
USE VertederoDW;
SET NOCOUNT ON;
DECLARE @desde INT = 20260927, @hasta INT = 20261104;

PRINT '== K4.a Bloqueos de cada domingo (¿el patron se repite o es un solo dia?) ==';
SELECT f.fecha, f.nombre_dia,
       SUM(CASE WHEN t.tipo = N'apertura' THEN 1 ELSE 0 END) AS aperturas,
       SUM(CASE WHEN t.tipo = N'bloqueo_llena' THEN 1 ELSE 0 END) AS bloqueos
FROM dbo.DimFecha f
LEFT JOIN (dbo.FactEventos e JOIN dbo.DimTipoEvento t ON t.tipo_evento_key = e.tipo_evento_key) ON e.fecha_key = f.fecha_key
WHERE f.fecha_key BETWEEN @desde AND @hasta AND f.dia_semana = 7
GROUP BY f.fecha, f.nombre_dia ORDER BY f.fecha;

PRINT '== K4.b Los 8 dias con mas bloqueos de todo el periodo ==';
SELECT TOP 8 f.fecha, f.nombre_dia, COUNT(*) AS bloqueos,
       CAST(100.0 * COUNT(*) / (SELECT COUNT(*) FROM dbo.FactEventos e2 JOIN dbo.DimTipoEvento t2 ON t2.tipo_evento_key = e2.tipo_evento_key
                                WHERE e2.fecha_key BETWEEN @desde AND @hasta AND t2.tipo = N'bloqueo_llena') AS DECIMAL(6,2)) AS pct_de_los_bloqueos
FROM dbo.FactEventos e
JOIN dbo.DimTipoEvento t ON t.tipo_evento_key = e.tipo_evento_key
JOIN dbo.DimFecha f ON f.fecha_key = e.fecha_key
WHERE e.fecha_key BETWEEN @desde AND @hasta AND t.tipo = N'bloqueo_llena'
GROUP BY f.fecha, f.nombre_dia ORDER BY bloqueos DESC, f.fecha;

PRINT '== K4.c Dias con al menos un bloqueo, por dia de la semana ==';
SELECT f.dia_semana, f.nombre_dia, COUNT(DISTINCT f.fecha_key) AS dias_con_bloqueo
FROM dbo.FactEventos e
JOIN dbo.DimTipoEvento t ON t.tipo_evento_key = e.tipo_evento_key
JOIN dbo.DimFecha f ON f.fecha_key = e.fecha_key
WHERE e.fecha_key BETWEEN @desde AND @hasta AND t.tipo = N'bloqueo_llena'
GROUP BY f.dia_semana, f.nombre_dia ORDER BY f.dia_semana;

PRINT '== K5.a Fin de semana separado en sabado y domingo (caneca x franja) ==';
SELECT c.nombre AS caneca, h.franja, f.nombre_dia,
       SUM(CASE WHEN t.tipo = N'apertura' THEN 1 ELSE 0 END) AS aperturas,
       SUM(CASE WHEN t.tipo = N'bloqueo_llena' THEN 1 ELSE 0 END) AS bloqueos,
       CAST(100.0 * SUM(CASE WHEN t.tipo = N'bloqueo_llena' THEN 1 ELSE 0 END)
            / NULLIF(SUM(CASE WHEN t.tipo IN (N'apertura', N'bloqueo_llena') THEN 1 ELSE 0 END), 0) AS DECIMAL(6,2)) AS tasa_bloqueo_pct
FROM dbo.FactEventos e
JOIN dbo.DimTipoEvento t ON t.tipo_evento_key = e.tipo_evento_key
JOIN dbo.DimCaneca c ON c.caneca_key = e.caneca_key
JOIN dbo.DimHora h ON h.hora_key = e.hora_key
JOIN dbo.DimFecha f ON f.fecha_key = e.fecha_key
WHERE e.fecha_key BETWEEN @desde AND @hasta AND f.dia_semana IN (6, 7) AND h.franja IN (N'Tarde', N'Noche')
GROUP BY c.nombre, h.franja, f.nombre_dia, f.dia_semana
ORDER BY c.nombre, h.franja DESC, f.dia_semana;

PRINT '== D1. Apoyo a la decision 1: bloqueos y lecturas criticas, domingo frente al resto ==';
SELECT CASE WHEN f.dia_semana = 7 THEN 'Domingo' ELSE 'Lunes a sabado' END AS grupo,
       COUNT(DISTINCT l.fecha_key) AS dias, COUNT(*) AS lecturas,
       CAST(AVG(1.0 * l.porcentaje) AS DECIMAL(6,2)) AS llenado_promedio_pct,
       CAST(100.0 * SUM(CASE WHEN l.porcentaje >= 90 THEN 1 ELSE 0 END) / COUNT(*) AS DECIMAL(6,2)) AS pct_lecturas_90_o_mas
FROM dbo.FactLecturas l JOIN dbo.DimFecha f ON f.fecha_key = l.fecha_key
WHERE l.fecha_key BETWEEN @desde AND @hasta
GROUP BY CASE WHEN f.dia_semana = 7 THEN 'Domingo' ELSE 'Lunes a sabado' END;

PRINT '== D2. Apoyo a la decision 2: lunes a sabado, de 18 a 23 h, por caneca ==';
WITH lec AS (
  SELECT c.nombre AS caneca, COUNT(DISTINCT l.fecha_key) AS dias, COUNT(*) AS lecturas,
         AVG(1.0 * l.porcentaje) AS llenado, SUM(CASE WHEN l.porcentaje >= 90 THEN 1 ELSE 0 END) AS l90
  FROM dbo.FactLecturas l
  JOIN dbo.DimCaneca c ON c.caneca_key = l.caneca_key
  JOIN dbo.DimFecha f ON f.fecha_key = l.fecha_key
  WHERE l.fecha_key BETWEEN @desde AND @hasta AND f.dia_semana <> 7 AND l.hora_key BETWEEN 18 AND 23
  GROUP BY c.nombre),
ev AS (
  SELECT c.nombre AS caneca,
         SUM(CASE WHEN t.tipo = N'apertura' THEN 1 ELSE 0 END) AS aperturas,
         SUM(CASE WHEN t.tipo = N'bloqueo_llena' THEN 1 ELSE 0 END) AS bloqueos
  FROM dbo.FactEventos e
  JOIN dbo.DimTipoEvento t ON t.tipo_evento_key = e.tipo_evento_key
  JOIN dbo.DimCaneca c ON c.caneca_key = e.caneca_key
  JOIN dbo.DimFecha f ON f.fecha_key = e.fecha_key
  WHERE e.fecha_key BETWEEN @desde AND @hasta AND f.dia_semana <> 7 AND e.hora_key BETWEEN 18 AND 23
  GROUP BY c.nombre)
SELECT lec.caneca, lec.dias, lec.lecturas,
       CAST(lec.llenado AS DECIMAL(6,2)) AS llenado_promedio_pct,
       CAST(100.0 * lec.l90 / lec.lecturas AS DECIMAL(6,2)) AS pct_lecturas_90_o_mas,
       ev.aperturas, ev.bloqueos,
       CAST(100.0 * ev.bloqueos / NULLIF(ev.aperturas + ev.bloqueos, 0) AS DECIMAL(6,2)) AS tasa_bloqueo_pct
FROM lec JOIN ev ON ev.caneca = lec.caneca
ORDER BY lec.caneca;

PRINT '== D2.b Bloqueos de lunes a sabado por franja (¿donde se concentran?) ==';
SELECT h.franja, COUNT(*) AS bloqueos,
       CAST(100.0 * COUNT(*) / SUM(COUNT(*)) OVER () AS DECIMAL(6,2)) AS pct
FROM dbo.FactEventos e
JOIN dbo.DimTipoEvento t ON t.tipo_evento_key = e.tipo_evento_key
JOIN dbo.DimHora h ON h.hora_key = e.hora_key
JOIN dbo.DimFecha f ON f.fecha_key = e.fecha_key
WHERE e.fecha_key BETWEEN @desde AND @hasta AND f.dia_semana <> 7 AND t.tipo = N'bloqueo_llena'
GROUP BY h.franja ORDER BY bloqueos DESC;
