/* =====================================================================
   06_datos_reales_esp32.sql
   Resumen de los datos REALES enviados por la ESP32 (fecha_key >= 20261106).
   Son pocos registros de pruebas con la maqueta: sirven para demostrar
   que el flujo funciona de punta a punta, no para sacar conclusiones.
   ===================================================================== */
USE VertederoDW;
SET NOCOUNT ON;
DECLARE @desde_real INT = 20261106;

PRINT '== R1. Lecturas reales por caneca ==';
SELECT c.nombre AS caneca, COUNT(*) AS lecturas,
       MIN(l.fecha_hora) AS primera, MAX(l.fecha_hora) AS ultima,
       CAST(AVG(1.0 * l.porcentaje) AS DECIMAL(6,2)) AS llenado_promedio_pct,
       MIN(l.porcentaje) AS pct_min, MAX(l.porcentaje) AS pct_max,
       MIN(l.distancia_mm) AS dist_min_mm, MAX(l.distancia_mm) AS dist_max_mm,
       SUM(CASE WHEN l.peso_g IS NULL THEN 1 ELSE 0 END) AS sin_peso
FROM dbo.FactLecturas l JOIN dbo.DimCaneca c ON c.caneca_key = l.caneca_key
WHERE l.fecha_key >= @desde_real
GROUP BY c.nombre ORDER BY 1;

PRINT '== R2. Eventos reales por caneca y tipo ==';
SELECT c.nombre AS caneca, t.tipo, COUNT(*) AS eventos
FROM dbo.FactEventos e
JOIN dbo.DimTipoEvento t ON t.tipo_evento_key = e.tipo_evento_key
JOIN dbo.DimCaneca c ON c.caneca_key = e.caneca_key
WHERE e.fecha_key >= @desde_real
GROUP BY c.nombre, t.tipo ORDER BY 1, 2;

PRINT '== R3. Lecturas y eventos reales por fecha ==';
SELECT f.fecha, f.nombre_dia,
       (SELECT COUNT(*) FROM dbo.FactLecturas l WHERE l.fecha_key = f.fecha_key) AS lecturas,
       (SELECT COUNT(*) FROM dbo.FactEventos e WHERE e.fecha_key = f.fecha_key) AS eventos
FROM dbo.DimFecha f
WHERE f.fecha_key >= @desde_real
  AND EXISTS (SELECT 1 FROM dbo.FactLecturas l WHERE l.fecha_key = f.fecha_key)
ORDER BY f.fecha;

PRINT '== R4. Alarmas reales ==';
SELECT COUNT(*) AS alarmas_reales FROM dbo.FactAlarmas WHERE fecha_key >= @desde_real;

PRINT '== R5. Estado actual: ultima lectura de cada caneca (lo que mostraria una pagina en vivo) ==';
SELECT c.nombre AS caneca, c.tipo_residuo, x.fecha_hora AS ultima_lectura, x.porcentaje, x.distancia_mm, s.estado
FROM dbo.DimCaneca c
CROSS APPLY (SELECT TOP 1 l.fecha_hora, l.porcentaje, l.distancia_mm, l.estado_key
             FROM dbo.FactLecturas l WHERE l.caneca_key = c.caneca_key ORDER BY l.fecha_hora DESC, l.lectura_key DESC) x
JOIN dbo.DimEstadoLlenado s ON s.estado_key = x.estado_key
WHERE c.caneca_key <> -1
ORDER BY c.nombre;
