# Diagnóstico local de Resolve

## Uso

Desde la raíz del repositorio, en macOS con Python 3.9 o posterior:

```sh
python3 scripts/diagnose_resolve.py
python3 scripts/diagnose_resolve.py --timeout 30 --app '/Applications/DaVinci Resolve/DaVinci Resolve.app'
python3 -m unittest discover -s tests -v
```

No requiere instalar paquetes. Usa el intérprete `ResolvePython` incluido desde Resolve 21.1; instalaciones anteriores devuelven `runtime_unavailable` y no están soportadas por este primer diagnóstico. Abrir Resolve antes de ejecutarlo; el comando no inicia ni cierra la aplicación ni cambia preferencias.

Devuelve JSON por stdout (`schema_version: 1`) y código 0 solo para `status: ok`; 1 indica diagnóstico fallido, 2 argumentos inválidos. El límite predeterminado es 15 segundos, configurable hasta 60. Un subproceso aísla la carga nativa y permite terminar la espera. No guarda archivos de resultados automáticamente; se pueden redirigir a `logs/`, excluido de Git.

## Alcance de lectura

Consulta el `Info.plist` de la aplicación, importa el módulo oficial y llama únicamente a `scriptapp("Resolve")`, `GetProductName()`, `GetVersion()`, `GetVersionString()` y `GetProjectManager()`. No enumera proyectos, no obtiene el proyecto actual ni sus nombres, no abre, crea, guarda o modifica proyectos/timelines, y no importa medios ni renderiza.

El acceso al gestor confirma conectividad básica; no prueba capacidades de edición. No se realizó una comparación de bases de datos antes/después: la garantía de alcance procede de las llamadas de lectura del código y su prueba con una API simulada que no expone mutaciones.

## Estados y diagnóstico

| Estado | Interpretación / siguiente acción |
| --- | --- |
| `ok` | API accesible y gestor disponible; versión real incluida |
| `unreachable` | No hay objeto Resolve; comprobar aplicación iniciada, sandbox y Preferences > System > General > External scripting (Local) |
| `installation_unavailable` | Revisar ruta de aplicación y acceso al plist |
| `runtime_unavailable` | No existe ResolvePython en esa instalación |
| `import_failed` | No se pudo importar el módulo oficial; revisar instalación/runtime |
| `project_manager_unavailable` | La API responde pero el gestor no está disponible |
| `api_failed` | Excepción en consulta de lectura; se registra solo el tipo |
| `timeout` | Espera agotada; comprobar estado de Resolve antes de repetir |
| `runtime_failed` / `invalid_response` | Fallo al iniciar, salida inesperada o terminación nativa; revisar instalación y permisos |
| `unsupported_platform` | Esta primera herramienta solo admite macOS |

No atribuir `unreachable` automáticamente a una preferencia: distintas restricciones producen el mismo síntoma. El comando no modifica esas preferencias. Suprime stdout/stderr nativo inesperado para no publicar datos privados.

## Resultado verificado — 2026-11-03 (America/Phoenix)

- Instalación (`Info.plist`): **21.1.2**.
- Inicialmente MCP informó Resolve detenido y el comando devolvió `unreachable`, código 1.
- Se inició Resolve mediante la herramienta de lanzamiento del MCP. No se solicitaron operaciones de proyecto.
- Con Resolve abierto, el comando dentro del sandbox siguió devolviendo `unreachable`.
- El mismo comando fuera del sandbox devolvió **`ok`**, código **0**: producto **DaVinci Resolve Studio**, versión API **21.1.2.10**, lista `[21, 1, 2, 10, ""]`, gestor accesible y Python incluido **3.14.4**.
- El estado MCP confirmó aplicación en ejecución, versión 21.1.2. Resolve se dejó abierto.
- Tres pruebas unitarias aprobadas: llamadas limitadas a lectura y ausencia de conexión; timeout, permisos, salida inválida y fallo nativo; validación del límite de espera.
- No se verificaron importación, edición, subtítulos ni render.

Fuentes técnicas locales verificadas en esta instalación: `Developer/Scripting/README.md` y `Developer/Scripting/DaVinciResolveScript.pyi`, bajo `/Library/Application Support/Blackmagic Design/DaVinci Resolve/`. La documentación instalada describe el intérprete incluido y las preferencias de acceso externo; el stub confirma las firmas de lectura utilizadas.
