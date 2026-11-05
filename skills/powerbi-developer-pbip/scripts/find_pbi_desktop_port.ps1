<#
.SYNOPSIS
    Detector de Puerto Local de Power BI Desktop (Analysis Services msmdsrv.exe)
.DESCRIPTION
    Identifica las instancias en ejecución del motor tabular de Power BI Desktop,
    localiza sus puertos TCP dinámicos y genera la cadena de conexión ADOMD.
.AUTHOR
    Rubén David Barrios Bello - Data Analyst & BI Developer
#>

[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   DIAGNOSTICO EN VIVO: PUERTOS LOCALES POWER BI DESKTOP   " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$procesos = Get-Process -Name "msmdsrv" -ErrorAction SilentlyContinue

if (-not $procesos) {
    Write-Host "[INFO] No se detecto ninguna instancia de 'msmdsrv.exe' activa." -ForegroundColor Yellow
    Write-Host "       Asegurate de que Power BI Desktop este abierto con un modelo cargado." -ForegroundColor Gray
    Write-Host "==========================================================" -ForegroundColor Cyan
    exit 0
}

foreach ($p in $procesos) {
    $conexiones = Get-NetTCPConnection -OwningProcess $p.Id -State Listen -ErrorAction SilentlyContinue |
                  Where-Object { $_.LocalAddress -in @("127.0.0.1", "::1") }

    if ($conexiones) {
        foreach ($conn in $conexiones) {
            Write-Host ""
            Write-Host "[+] Instancia Local Encontrada:" -ForegroundColor Green
            Write-Host "    - PID Proceso:       $($p.Id)"
            Write-Host "    - Puerto TCP Local:  $($conn.LocalPort)"
            Write-Host "    - Cadena Conexion:   Data Source=localhost:$($conn.LocalPort);" -ForegroundColor White
        }
    } else {
        Write-Host ""
        Write-Host "[!] Proceso msmdsrv.exe encontrado (PID: $($p.Id)), pero sin puertos TCP en escucha." -ForegroundColor Yellow
    }
}
Write-Host ""
Write-Host "==========================================================" -ForegroundColor Cyan
