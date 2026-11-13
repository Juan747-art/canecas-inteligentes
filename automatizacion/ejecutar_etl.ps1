<#
  Ejecuta el paquete maestro del ETL (00_Maestro.dtsx) con dtexec y deja una linea
  de registro por ejecucion: hora, resultado, duracion y filas cargadas.

  REQUISITO: dtexec solo ejecuta los flujos de datos si en este equipo esta instalado
  Integration Services de SQL Server 2022 edicion Developer, Standard o Enterprise.
  Con solo SQL Server Express falla con el error 0xC000F427.

  La contrasena de SQL Server NO esta en este archivo:
    - el paquete usa la que quedo cifrada en el .ispac con la cuenta de Windows;
    - para leer las filas cargadas se usa la credencial cifrada que crea
      guardar_credencial.ps1 (fuera del repositorio, en %LOCALAPPDATA%\Canecas).

  Uso manual:   powershell -ExecutionPolicy Bypass -File .\ejecutar_etl.ps1
#>
param(
  [string]$Ispac   = "$env:USERPROFILE\Documents\VertederoETL\ssis\VertederoETL\VertederoETL\bin\Development\VertederoETL.ispac",
  [string]$Paquete = "00_Maestro.dtsx",
  [string]$DtExec  = "C:\Program Files\Microsoft SQL Server\160\DTS\Binn\DTExec.exe",
  [string]$Servidor = "localhost\SQLEXPRESS",
  [string]$CarpetaLog = "$PSScriptRoot\logs"
)
$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force $CarpetaLog | Out-Null
$log = Join-Path $CarpetaLog ("etl_{0:yyyy-MM}.log" -f (Get-Date))
function Registrar([string]$linea) { Add-Content -Path $log -Value $linea -Encoding utf8 }

# Evita que dos ejecuciones se crucen si una tarda mas que el intervalo de la tarea
$mutex = New-Object System.Threading.Mutex($false, 'Global\CanecasETL')
if (-not $mutex.WaitOne(0)) {
  Registrar ("{0:yyyy-MM-dd HH:mm:ss} | OMITIDA | otra ejecucion del ETL sigue en curso" -f (Get-Date))
  exit 0
}
try {
  $inicio = Get-Date
  if (-not (Test-Path $DtExec)) { Registrar ("{0:yyyy-MM-dd HH:mm:ss} | ERROR | no existe $DtExec" -f $inicio); exit 2 }
  if (-not (Test-Path $Ispac))  { Registrar ("{0:yyyy-MM-dd HH:mm:ss} | ERROR | no existe $Ispac (compile el proyecto en Visual Studio)" -f $inicio); exit 2 }

  $salida = & $DtExec /Project $Ispac /Package $Paquete /Reporting E 2>&1
  $codigo = $LASTEXITCODE
  $seg = [math]::Round(((Get-Date) - $inicio).TotalSeconds, 1)
  $resultado = if ($codigo -eq 0) { 'OK' } else { 'ERROR' }

  # Filas cargadas por el ultimo lote, leidas del registro del propio ETL
  $filas = 'filas: n/d (ejecute guardar_credencial.ps1 una vez)'
  $cred = Join-Path $env:LOCALAPPDATA 'Canecas\sql_cred.xml'
  if (Test-Path $cred) {
    try {
      $c = Import-Clixml $cred
      $env:SQLCMDPASSWORD = $c.GetNetworkCredential().Password
      $q = "SET NOCOUNT ON; DECLARE @l INT = (SELECT MAX(id_lote) FROM etl.LogEjecucion); " +
           "SELECT CONCAT('lote ', @l, ' ', MAX(CASE WHEN tabla = N'(lote)' THEN estado END), " +
           "' | lecturas nuevas ', ISNULL(MAX(CASE WHEN tabla = N'FactLecturas' THEN filas_insertadas END), 0), " +
           "' | eventos nuevos ', ISNULL(MAX(CASE WHEN tabla = N'FactEventos' THEN filas_insertadas END), 0), " +
           "' | alarmas ins/act ', ISNULL(MAX(CASE WHEN tabla = N'FactAlarmas' THEN ISNULL(filas_insertadas, 0) + ISNULL(filas_actualizadas, 0) END), 0), " +
           "' | rechazadas ', ISNULL(SUM(CASE WHEN tabla <> N'(lote)' THEN filas_rechazadas END), 0), " +
           "' | total FactLecturas ', (SELECT COUNT(*) FROM dbo.FactLecturas)) FROM etl.LogEjecucion WHERE id_lote = @l;"
      $r = & sqlcmd -S $Servidor -U $c.UserName -C -d VertederoDW -h -1 -W -Q $q 2>&1
      if ($LASTEXITCODE -eq 0) { $filas = ($r | Select-Object -First 1).ToString().Trim() } else { $filas = 'filas: n/d (no se pudo consultar el registro)' }
    } finally { Remove-Item Env:SQLCMDPASSWORD -ErrorAction SilentlyContinue }
  }

  $detalle = ''
  if ($codigo -ne 0) {
    $err = $salida | Where-Object { $_ -match 'Description:' } | Select-Object -First 1
    $detalle = " | " + (("$err" -replace '\s+', ' ').Trim())
  }
  Registrar ("{0:yyyy-MM-dd HH:mm:ss} | {1} | {2} s | {3}{4}" -f $inicio, $resultado, $seg, $filas, $detalle)
  exit $codigo
}
finally { $mutex.ReleaseMutex(); $mutex.Dispose() }
