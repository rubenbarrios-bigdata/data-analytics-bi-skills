# Guía de Arquitectura de Carpetas y Ficheros en Formato PBIP

El formato **Power BI Project (`.pbip`)** es el estándar abierto de Microsoft que desglosa un reporte de Power BI en archivos de texto legibles, versionables y compatibles con Git.

---

## 1. Árbol de Directorios Oficial de un Proyecto PBIP

```
MiProyectoAnalytics/
├── MiProyectoAnalytics.pbip               <-- Archivo puntero raíz que abre Power BI Desktop
│
├── MiProyectoAnalytics.Report/            <-- Directorio de Capa Visual y Páginas
│   ├── definition.pbir                    <-- Archivo JSON puntero de conexión al SemanticModel
│   ├── report.json                        <-- Definición de páginas, visuales, filtros y layouts
│   └── StaticResources/                   <-- Imágenes, iconos y temas personalizados
│       └── SharedResources/
│
└── MiProyectoAnalytics.SemanticModel/     <-- Directorio del Modelo de Datos Tabular
    ├── definition.pbism                   <-- Puntero de configuración del modelo semántico
    ├── definition/                        <-- Definición modular en TMDL (recomendado)
    │   ├── model.tmdl                     <-- Propiedades globales, cultura y configuración
    │   ├── database.tmdl                  <-- Compatibilidad y nivel de motor
    │   ├── tables/                        <-- Una carpeta con un fichero .tmdl por cada tabla
    │   │   ├── Clientes.tmdl
    │   │   ├── Calendario.tmdl
    │   │   └── Ventas.tmdl
    │   └── relationships.tmdl             <-- Definición de relaciones y cardinalidades
    └── model.bim                          <-- Esquema JSON TMSL clásico (si no usa TMDL)
```

---

## 2. Contenido del Archivo `definition.pbir`

Define si el reporte se conecta a un SemanticModel local (dentro del mismo PBIP) o a un SemanticModel remoto en la nube (Power BI Service / Fabric):

```json
{
  "version": "1.0",
  "datasetReference": {
    "byPath": {
      "path": "../MiProyectoAnalytics.SemanticModel"
    },
    "byConnection": null
  }
}
```

---

## 3. Contenido de `definition.pbism`

Configura el formato de serialización del modelo (TMDL o TMSL):

```json
{
  "version": "1.0",
  "settings": {
    "tmdl": true
  }
}
```

---

## 4. Beneficios Clave para Equipos de Datos
1. **Resolución de Conflictos Granular:** Si dos analistas crean medidas distintas en la tabla `Ventas`, el diff de Git muestra líneas exactas en `tables/Ventas.tmdl`, permitiendo merges automáticos sin corruptelas.
2. **Auditorías de Código (Code Review):** Los revisores pueden inspeccionar DAX, nombres de columnas y fórmulas directamente en la interfaz de Pull Request de Azure DevOps o GitHub.
3. **Automatización CI/CD:** Herramientas de terminal o scripts pueden inspeccionar, validar o modificar metadatos sin abrir la aplicación gráfica Power BI Desktop.

