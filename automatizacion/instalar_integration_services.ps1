<#
  Instala la caracteristica Integration Services de SQL Server 2022 Developer Edition.
  Hace falta para que dtexec pueda ejecutar los flujos de datos del ETL fuera de Visual Studio
  (error 0xC000F427 con solo SQL Server Express).

  - No crea otra instancia del motor ni toca las bases de datos: solo agrega la caracteristica
    compartida "IS" (Integration Services).
  - Developer Edition es gratuita; su licencia es para desarrollo y pruebas.
  - Necesita permisos de administrador: el script los pide con una ventana de Windows (UAC).

  Usa la imagen ISO oficial (1,1 GB) de download.microsoft.com, guardada en C:\SQL2022Dev.
  El instalador web SQL2022-SSEI-Dev.exe fallaba al arrancar en este equipo
  (FatalActivityException en StartupBootstrapActivity), por eso se usa la ISO.

  Uso: powershell -ExecutionPolicy Bypass -File .\instalar_integration_services.ps1
  Resultado: C:\SQL2022Dev\instalacion.log
#>
$ErrorActionPreference = 'Stop'
$base = 'C:\SQL2022Dev'
$iso  = Join-Path $base 'SQLServer2022-x64-ENU-Dev.iso'
$url  = 'https://download.microsoft.com/download/3/8/d/38de7036-2433-4207-8eae-06e247e17b25/SQLServer2022-x64-ENU-Dev.iso'
$log  = Join-Path $base 'instalacion.log'
$es_admin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
  [Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $es_admin) {
  Start-Process powershell.exe -Verb RunAs -Wait -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`""
  if (Test-Path $log) { Get-Content $log -Tail 20 }
  exit
}

New-Item -ItemType Directory -Force $base | Out-Null
function Escribir($t) { $l = "{0:yyyy-MM-dd HH:mm:ss}  {1}" -f (Get-Date), $t; $l; Add-Content -Path $log -Value $l -Encoding UTF8 }

$montada = $false
try {
  if (-not (Test-Path $iso) -or (Get-Item $iso).Length -lt 1GB) {
    Escribir 'Descargando la ISO de SQL Server 2022 Developer (~1,1 GB)...'
    & curl.exe -sS -L -o $iso $url
    if ($LASTEXITCODE -ne 0) { throw "La descarga fallo (curl $LASTEXITCODE)" }
  }

  Escribir "Montando $iso"
  $img = Mount-DiskImage -ImagePath $iso -PassThru
  $montada = $true
  $letra = ($img | Get-Volume).DriveLetter
  $setup = "${letra}:\setup.exe"

  $firma = Get-AuthenticodeSignature $setup
  if ($firma.Status -ne 'Valid' -or $firma.SignerCertificate.Subject -notmatch 'O=Microsoft Corporation') {
    throw "setup.exe no tiene una firma valida de Microsoft ($($firma.Status))"
  }
  Escribir "setup.exe firmado por Microsoft. Instalando Integration Services (FEATURES=IS)..."

  $args_setup = @('/Q', '/ACTION=Install', '/FEATURES=IS', '/IACCEPTSQLSERVERLICENSETERMS',
                  '/UpdateEnabled=False', '/SUPPRESSPRIVACYSTATEMENTNOTICE')
  $p = Start-Process $setup -ArgumentList $args_setup -Wait -PassThru
  Escribir "setup.exe termino con codigo $($p.ExitCode) (0 = correcto; 3010 = correcto, hay que reiniciar)"

  $resumen = 'C:\Program Files\Microsoft SQL Server\160\Setup Bootstrap\Log\Summary.txt'
  if (Test-Path $resumen) { Get-Content $resumen -TotalCount 12 | ForEach-Object { Escribir "  $_" } }
} catch {
  Escribir "ERROR: $($_.Exception.Message)"
} finally {
  if ($montada) { Dismount-DiskImage -ImagePath $iso | Out-Null; Escribir 'ISO desmontada.' }
}
Escribir 'Fin. Puede cerrar esta ventana.'
Start-Sleep -Seconds 8
