# Actualización automática de los datos

Estado al 13 de noviembre de 2026: **tramo A activo** (ETL cada 5 minutos). Tramo B (Power BI) pendiente.

## Tramo A: de `Vertedero` a `VertederoDW` (ETL en SSIS)

La tarea **«Canecas - ETL VertederoDW»** del Programador de tareas de Windows ejecuta `ejecutar_etl.ps1` cada 5 minutos. El script corre `00_Maestro.dtsx` con `dtexec`, sin Visual Studio, y deja una línea en `logs\etl_AAAA-MM.log`:

```
2026-11-13 01:06:01 | OK | 21.8 s | lote 70 OK | lecturas nuevas 0 | eventos nuevos 0 | alarmas ins/act 0 | rechazadas 0 | total FactLecturas 1000933
```

Condiciones:

- Corre con el usuario de Windows del proyecto y **solo con la sesión iniciada**. La contraseña del paquete está cifrada con la clave de ese usuario (`EncryptSensitiveWithUserKey`).
- Si una ejecución sigue en curso, la siguiente se omite y queda anotada como `OMITIDA`.
- Usa el `.ispac` de `Documents\VertederoETL\...\bin\Development`. **Si cambian un paquete, recompilen el proyecto en Visual Studio** (Compilar → Compilar solución); si no, la tarea sigue usando la versión anterior.

### Qué se comprobó

| Comprobación | Resultado |
|---|---|
| `dtexec` con solo SQL Server Express | Falla en el primer flujo de datos con `0xC000F427` (exige Integration Services Standard o superior). No cambió datos; dejó dos filas `Error` en `etl.LogEjecucion`. |
| Instalación de Integration Services | SQL Server 2022 **Developer Edition**, característica `IS`, desde la ISO oficial (`instalar_integration_services.ps1`). Resultado «Passed»; edición registrada: Developer Edition 16.0.1000.6. No se creó otra instancia del motor. El instalador web `SQL2022-SSEI-Dev.exe` se cerraba al arrancar en este equipo. |
| Ejecución manual con `dtexec` | Lote 61: OK, 17 s, 0 filas nuevas (el DW ya estaba al día). |
| Primera ejecución programada | Lote 70, 13/11/2026 01:06: OK, 21,8 s, 0 filas nuevas. |
| Ejecutar dos veces | No duplica: el ETL es incremental por marca de agua (`etl.ControlCarga`) y un índice único por identificador de origen impide duplicados. No recarga el millón salvo que `RecargaCompleta` sea verdadero. |
| De punta a punta | 13/11/2026 01:09: lectura de prueba enviada a `servidor_canecas.py` (`/lectura`, 20/40/60 %, ids 1.000.934–1.000.936). Ejecución programada de las 01:11 (lote 79): «lecturas nuevas 3», `FactLecturas` de 1.000.933 a 1.000.936, 0 rechazadas. Esas 3 filas son de prueba, no de la maqueta. |

### Archivos

| Archivo | Para qué sirve |
|---|---|
| `ejecutar_etl.ps1` | Ejecuta el maestro con `dtexec` y escribe una línea por ejecución. |
| `registrar_tarea.ps1` | Crea o reemplaza la tarea (parámetro `-Minutos`, por defecto 5). |
| `guardar_credencial.ps1` | Guarda cifrada (DPAPI) la credencial de SQL Server en `%LOCALAPPDATA%\Canecas`, fuera del repositorio. Ya está hecha en este equipo. |
| `instalar_integration_services.ps1` | Instala Integration Services (Developer). Ya está hecha en este equipo. |
| `logs\` | Registros mensuales. No se suben al repositorio. |

### Operación

- Ver el estado: Programador de tareas → Biblioteca → «Canecas - ETL VertederoDW» → pestaña Historial, o abrir el último `logs\etl_*.log`.
- Pausar: clic derecho sobre la tarea → Deshabilitar.
- Quitar: `Unregister-ScheduledTask -TaskName 'Canecas - ETL VertederoDW' -Confirm:$false`.

## Tramo B: de `VertederoDW` a Power BI

Ver `powerbi/LEEME.md`.
