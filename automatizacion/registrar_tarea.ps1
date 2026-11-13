<#
  Crea (o reemplaza) la tarea del Programador de tareas de Windows que ejecuta el ETL
  cada pocos minutos.

  La tarea corre con el usuario actual de Windows y solo mientras ese usuario tenga la
  sesion iniciada: la contrasena del paquete SSIS esta cifrada con la clave de ese
  usuario (EncryptSensitiveWithUserKey) y no se puede descifrar desde otra cuenta.
  No hace falta tener Visual Studio abierto.

  Uso:      powershell -ExecutionPolicy Bypass -File .\registrar_tarea.ps1
            powershell -ExecutionPolicy Bypass -File .\registrar_tarea.ps1 -Minutos 10
  Quitar:   Unregister-ScheduledTask -TaskName 'Canecas - ETL VertederoDW' -Confirm:$false
#>
param([int]$Minutos = 5, [string]$Nombre = 'Canecas - ETL VertederoDW')
$script = Join-Path $PSScriptRoot 'ejecutar_etl.ps1'
$accion = New-ScheduledTaskAction -Execute 'powershell.exe' `
  -Argument "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$script`""
$disparador = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) `
  -RepetitionInterval (New-TimeSpan -Minutes $Minutos)
$ajustes = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -StartWhenAvailable `
  -ExecutionTimeLimit (New-TimeSpan -Minutes 30) -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName $Nombre -Action $accion -Trigger $disparador -Settings $ajustes -Principal $principal `
  -Description 'Ejecuta 00_Maestro.dtsx (ETL de Vertedero a VertederoDW) y registra el resultado en automatizacion\logs.' -Force | Out-Null
"Tarea '$Nombre' registrada: cada $Minutos minutos. Registro en $PSScriptRoot\logs"
