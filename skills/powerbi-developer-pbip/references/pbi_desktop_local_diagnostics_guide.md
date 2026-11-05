# Guía de Diagnóstico en Vivo: Conexión Local a Power BI Desktop (msmdsrv.exe)

Cada vez que Power BI Desktop abre un archivo `.pbip` o `.pbix`, ejecuta en segundo plano una instancia dedicada de **Analysis Services Tabular (`msmdsrv.exe`)**. Conectarse a esta instancia permite auditar medidas, rendimiento de memoria y ejecutar consultas DAX desde la terminal.

---

## 1. Detección del Proceso y Puerto Dinámico

Power BI Desktop asigna un puerto TCP aleatorio en cada ejecución para aislar diferentes instancias.

### Script de Detección Rápida en PowerShell
```powershell
$pbiProcess = Get-Process -Name "msmdsrv" -ErrorAction SilentlyContinue

if ($pbiProcess) {
    foreach ($proc in $pbiProcess) {
        $tcpConn = Get-NetTCPConnection -OwningProcess $proc.Id -State Listen -ErrorAction SilentlyContinue |
                   Where-Object { $_.LocalAddress -in @("127.0.0.1", "::1") } |
                   Select-Object -First 1

        if ($tcpConn) {
            Write-Host "[OK] Instancia Analysis Services detectada:" -ForegroundColor Green
            Write-Host "     PID:    $($proc.Id)"
            Write-Host "     Puerto: $($tcpConn.LocalPort)"
            Write-Host "     Cadena de Conexión: Data Source=localhost:$($tcpConn.LocalPort)"
        }
    }
} else {
    Write-Host "[INFO] Power BI Desktop no está en ejecución actualmente." -ForegroundColor Yellow
}
```

---

## 2. Consultas a Dynamic Management Views (DMVs)

Una vez conocido el puerto (ej. `localhost:54321`), se pueden consultar las vistas de administración del sistema mediante DAX Studio, Python (`pyadomd`) o PowerShell:

- **Listar todas las medidas del modelo:**
  ```sql
  SELECT [TableID], [Name], [Expression], [FormatString]
  FROM $SYSTEM.TMSCHEMA_MEASURES
  ```
- **Auditoría de Consumo de Memoria por Columna:**
  ```sql
  SELECT [DIMENSION_NAME], [COLUMN_ENCODING], [DICTIONARY_SIZE], [USED_SIZE]
  FROM $SYSTEM.DISCOVER_STORAGE_TABLE_COLUMNS
  ```
- **Ejecución directa de consultas DAX:**
  ```dax
  EVALUATE
  SUMMARIZECOLUMNS(
      'Clientes'[Segmento],
      "Total Ventas", [Total Ventas],
      "Margen Pct", [Margen Operativo Pct]
  )
  ```

