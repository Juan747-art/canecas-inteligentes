/* =====================================================================
   00_alcance_y_calidad.sql
   Proyecto Canecas Inteligentes - consultas sobre VertederoDW
   Alcance de los datos, conciliacion con el origen, valores faltantes,
   valores atipicos y tamano de los grupos que se comparan.

   Periodo SIMULADO: 2026-09-27 a 2026-11-04 (fecha_key 20260927-20261104)
   Datos REALES (ESP32): desde 2026-11-06 (fecha_key >= 20261106)
   ===================================================================== */
USE VertederoDW;
SET NOCOUNT ON;
DECLARE @desde INT = 20260927, @hasta INT = 20261104;

PRINT '== A. Lecturas por origen (simulado / real) ==';
SELECT CASE WHEN l.fecha_key BETWEEN @desde AND @hasta THEN 'Simulado' ELSE 'Real ESP32' END AS origen,
       COUNT(*) AS lecturas,
       MIN(l.fecha_hora) AS primera, MAX(l.fecha_hora) AS ultima,
       COUNT(DISTINCT l.fecha_key) AS dias_con_datos
FROM dbo.FactLecturas l
GROUP BY CASE WHEN l.fecha_key BETWEEN @desde AND @hasta THEN 'Simulado' ELSE 'Real ESP32' END;

PRINT '== B. Eventos por origen y tipo ==';
SELECT CASE WHEN e.fecha_key BETWEEN @desde AND @hasta THEN 'Simulado' ELSE 'Real ESP32' END AS origen,
       t.tipo, COUNT(*) AS eventos, MIN(e.porcentaje) AS pct_min, MAX(e.porcentaje) AS pct_max
FROM dbo.FactEventos e JOIN dbo.DimTipoEvento t ON t.tipo_evento_key = e.tipo_evento_key
GROUP BY CASE WHEN e.fecha_key BETWEEN @desde AND @hasta THEN 'Simulado' ELSE 'Real ESP32' END, t.tipo
ORDER BY 1, 2;

PRINT '== C. Conciliacion origen (Vertedero) vs data warehouse ==';
SELECT 'Lecturas' AS tabla, (SELECT COUNT(*) FROM Vertedero.dbo.Lecturas) AS filas_origen,
       (SELECT COUNT(*) FROM dbo.FactLecturas) AS filas_dw,
       (SELECT COUNT(*) FROM etl.Rechazo_FactLecturas) AS rechazadas
UNION ALL SELECT 'Eventos', (SELECT COUNT(*) FROM Vertedero.dbo.Eventos), (SELECT COUNT(*) FROM dbo.FactEventos),
       (SELECT COUNT(*) FROM etl.Rechazo_FactEventos)
UNION ALL SELECT 'Alarmas', (SELECT COUNT(*) FROM Vertedero.dbo.Alarmas), (SELECT COUNT(*) FROM dbo.FactAlarmas),
       (SELECT COUNT(*) FROM etl.Rechazo_FactAlarmas);

PRINT '== D. Duplicados y claves desconocidas (-1) en FactLecturas ==';
SELECT COUNT(*) AS filas, COUNT(DISTINCT id_lectura_origen) AS ids_distintos,
       SUM(CASE WHEN fecha_key = -1 OR hora_key = -1 OR caneca_key = -1 OR estado_key = -1 THEN 1 ELSE 0 END) AS con_clave_desconocida
FROM dbo.FactLecturas;

PRINT '== E. Valores faltantes por origen y caneca ==';
SELECT CASE WHEN l.fecha_key BETWEEN @desde AND @hasta THEN 'Simulado' ELSE 'Real ESP32' END AS origen,
       c.nombre AS caneca, COUNT(*) AS lecturas,
       SUM(CASE WHEN l.distancia_mm IS NULL THEN 1 ELSE 0 END) AS sin_distancia,
       CAST(100.0 * SUM(CASE WHEN l.distancia_mm IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS DECIMAL(6,3)) AS pct_sin_distancia,
       SUM(CASE WHEN l.peso_g IS NULL THEN 1 ELSE 0 END) AS sin_peso
FROM dbo.FactLecturas l JOIN dbo.DimCaneca c ON c.caneca_key = l.caneca_key
GROUP BY CASE WHEN l.fecha_key BETWEEN @desde AND @hasta THEN 'Simulado' ELSE 'Real ESP32' END, c.nombre
ORDER BY 1, 2;

PRINT '== F. Rangos (posibles atipicos) por origen ==';
SELECT CASE WHEN l.fecha_key BETWEEN @desde AND @hasta THEN 'Simulado' ELSE 'Real ESP32' END AS origen,
       MIN(l.porcentaje) AS pct_min, MAX(l.porcentaje) AS pct_max,
       MIN(l.distancia_mm) AS dist_min_mm, MAX(l.distancia_mm) AS dist_max_mm,
       MIN(l.peso_g) AS peso_min_g, MAX(l.peso_g) AS peso_max_g,
       SUM(CASE WHEN l.porcentaje < 0 OR l.porcentaje > 100 THEN 1 ELSE 0 END) AS pct_fuera_de_0_100
FROM dbo.FactLecturas l
GROUP BY CASE WHEN l.fecha_key BETWEEN @desde AND @hasta THEN 'Simulado' ELSE 'Real ESP32' END;

PRINT '== G. Llenado de las lecturas SIN distancia frente a las validas (periodo simulado) ==';
SELECT l.lectura_valida, COUNT(*) AS lecturas,
       CAST(AVG(1.0 * l.porcentaje) AS DECIMAL(6,2)) AS llenado_promedio_pct
FROM dbo.FactLecturas l
WHERE l.fecha_key BETWEEN @desde AND @hasta
GROUP BY l.lectura_valida;

PRINT '== H. Coherencia de eventos con la regla del 95 % (periodo simulado) ==';
SELECT t.tipo,
       SUM(CASE WHEN e.porcentaje >= 95 THEN 1 ELSE 0 END) AS con_95_o_mas,
       SUM(CASE WHEN e.porcentaje <  95 THEN 1 ELSE 0 END) AS con_menos_de_95
FROM dbo.FactEventos e JOIN dbo.DimTipoEvento t ON t.tipo_evento_key = e.tipo_evento_key
WHERE e.fecha_key BETWEEN @desde AND @hasta
GROUP BY t.tipo ORDER BY 1;

PRINT '== I. Tamano de los grupos comparados (periodo simulado) ==';
PRINT '-- I.1 dias por tipo de dia y por dia de la semana';
SELECT f.tipo_dia, f.dia_semana, f.nombre_dia, COUNT(DISTINCT l.fecha_key) AS dias, COUNT(*) AS lecturas
FROM dbo.FactLecturas l JOIN dbo.DimFecha f ON f.fecha_key = l.fecha_key
WHERE l.fecha_key BETWEEN @desde AND @hasta
GROUP BY f.tipo_dia, f.dia_semana, f.nombre_dia ORDER BY f.dia_semana;
PRINT '-- I.2 lecturas por caneca';
SELECT c.nombre AS caneca, c.tipo_residuo, COUNT(*) AS lecturas
FROM dbo.FactLecturas l JOIN dbo.DimCaneca c ON c.caneca_key = l.caneca_key
WHERE l.fecha_key BETWEEN @desde AND @hasta
GROUP BY c.nombre, c.tipo_residuo ORDER BY 1;
PRINT '-- I.3 lecturas por franja horaria';
SELECT h.franja, MIN(h.hora_key) AS hora_desde, MAX(h.hora_key) AS hora_hasta, COUNT(*) AS lecturas
FROM dbo.FactLecturas l JOIN dbo.DimHora h ON h.hora_key = l.hora_key
WHERE l.fecha_key BETWEEN @desde AND @hasta
GROUP BY h.franja ORDER BY 2;
PRINT '-- I.4 dias incompletos (menos de 25.920 lecturas = 3 canecas x 8.640 lecturas)';
SELECT f.fecha, f.nombre_dia, COUNT(*) AS lecturas, MAX(l.fecha_hora) AS ultima_lectura
FROM dbo.FactLecturas l JOIN dbo.DimFecha f ON f.fecha_key = l.fecha_key
WHERE l.fecha_key BETWEEN @desde AND @hasta
GROUP BY f.fecha, f.nombre_dia HAVING COUNT(*) < 25920;
