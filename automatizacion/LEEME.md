# Actualización automática de los datos

Estado al 13 de noviembre de 2026: **preparada, no activada**.

## Tramo A: de `Vertedero` a `VertederoDW` (ETL en SSIS)

### Qué se comprobó

| Comprobación | Resultado |
|---|---|
| ¿`dtexec` está instalado? | Sí: `C:\Program Files\Microsoft SQL Server\160\DTS\Binn\DTExec.exe` (también hay versiones 130 y 150). |
| ¿Puede ejecutar `00_Maestro.dtsx`? | **No en este equipo.** Se conecta y ejecuta las tareas de control, pero el primer flujo de datos falla con `0xC000F427: To run a SSIS package outside of SQL Server Data Tools you must install Standard Edition (64-bit) of Integration Services or higher`. Solo hay SQL Server Express y no hay Integration Services de servidor instalado. |
| ¿La prueba cambió datos? | No. `FactLecturas` 1.000.933, `FactEventos` 7.741 y `FactAlarmas` 3 antes y después. Quedaron dos filas con estado `Error` en `etl.LogEjecucion` (id 59 y 60). |
| ¿Qué pasa al ejecutar el ETL dos veces? | No se pudo repetir con `dtexec`. El registro del ETL muestra que ya ocurrió desde Visual Studio: los lotes 41 y 50 (12 de noviembre) extrajeron 0 lecturas y 0 eventos y los conteos no cambiaron. El ETL es incremental por marca de agua (`etl.ControlCarga`) y un índice único por identificador de origen impide duplicados. No borra ni recarga el millón, salvo que `RecargaCompleta` sea verdadero. |

### Qué falta para activarlo

1. Instalar la característica **Integration Services** de **SQL Server 2022 Developer Edition** (gratuita; licencia para desarrollo y pruebas, no para producción). No hace falta crear otra instancia del motor.
2. Compilar el proyecto en Visual Studio (Compilar → Compilar solución) para tener el `.ispac` actualizado.
3. Ejecutar una vez `guardar_credencial.ps1` (para que el registro incluya las filas cargadas).
4. Probar a mano: `powershell -ExecutionPolicy Bypass -File .\ejecutar_etl.ps1` y revisar `logs\etl_AAAA-MM.log`.
5. Registrar la tarea: `powershell -ExecutionPolicy Bypass -File .\registrar_tarea.ps1` (cada 5 minutos).
6. Verificar de punta a punta: anotar `SELECT COUNT(*) FROM VertederoDW.dbo.FactLecturas`, encender la ESP32 y el servidor Python, esperar una ejecución de la tarea y confirmar que el conteo subió.

### Archivos

| Archivo | Para qué sirve |
|---|---|
| `ejecutar_etl.ps1` | Ejecuta el maestro con `dtexec` y escribe una línea por ejecución: hora, resultado, duración, lote y filas nuevas. |
| `registrar_tarea.ps1` | Crea la tarea «Canecas - ETL VertederoDW» en el Programador de tareas. |
| `guardar_credencial.ps1` | Guarda cifrada (DPAPI) la credencial de SQL Server fuera del repositorio. |
| `logs\` | Registros mensuales. No se suben al repositorio. |

Los scripts **no se han probado de punta a punta** porque `dtexec` todavía no puede ejecutar los flujos de datos en este equipo.

## Tramo B: de `VertederoDW` a Power BI

Ver `powerbi/LEEME.md`.
