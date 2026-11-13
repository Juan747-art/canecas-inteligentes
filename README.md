# Canecas Inteligentes

Proyecto de Gestión del Conocimiento (PGC): módulo «vertedero» de una maqueta de ciudad inteligente.
Juan Diego Lozano y Deivid Real · Big Data, séptimo semestre, Sede Chía.

**Sitio:** https://juan747-art.github.io/canecas-inteligentes/

## Contenido

| Carpeta | Contenido |
|---|---|
| `docs/` | Sitio web (GitHub Pages). `docs/js/config.js` tiene la URL del dashboard de Power BI. |
| `docs/img/evidencias/` | Fotos y capturas; los nombres esperados están en `docs/js/datos.js`. |
| `consultas/` | Consultas T-SQL sobre `VertederoDW` que producen cada valor del sitio, y sus resultados en `consultas/resultados/`. |
| `automatizacion/` | Scripts para ejecutar el ETL de SSIS con el Programador de tareas de Windows. |
| `powerbi/` | Lista de visuales del dashboard y pasos de publicación y actualización. |

## Repetir los análisis

En SSMS, conectado a la instancia con `VertederoDW`, abrir y ejecutar en orden los archivos `consultas/00` a `06`. Los valores deben coincidir con los de `consultas/resultados/` mientras no cambien los datos del período simulado (27 de septiembre a 4 de noviembre de 2026).

## Datos

Casi todos los datos son simulados (1.000.000 de lecturas). Las lecturas reales de la ESP32 son 933. El peso es siempre simulado. El detalle está en el sitio, sección «Gestión de los datos».

No se incluyen en el repositorio los CSV de datos, el archivo `.pbix` ni ningún archivo con contraseñas.
