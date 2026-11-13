<#
  Guarda, UNA sola vez, el usuario y la contrasena de SQL Server que usa ejecutar_etl.ps1
  para leer cuantas filas cargo cada ejecucion.

  La contrasena queda cifrada con la cuenta de Windows (DPAPI) en
  %LOCALAPPDATA%\Canecas\sql_cred.xml, fuera del repositorio. Solo este usuario de
  Windows, en este computador, puede descifrarla.

  Uso:   powershell -ExecutionPolicy Bypass -File .\guardar_credencial.ps1
#>
$carpeta = Join-Path $env:LOCALAPPDATA 'Canecas'
New-Item -ItemType Directory -Force $carpeta | Out-Null
$cred = Get-Credential -Message 'Usuario y contrasena de SQL Server (los mismos de SSMS)'
if ($cred) {
  $cred | Export-Clixml (Join-Path $carpeta 'sql_cred.xml')
  "Credencial guardada y cifrada en $carpeta\sql_cred.xml"
}
