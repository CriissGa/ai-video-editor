# Primer flujo de edición

## Uso

Con Resolve abierto en macOS (Studio 21.1.2.10 verificado), desde la raíz:

```sh
python3 scripts/edit_video.py plans/first-draft.json
python3 scripts/edit_video.py plans/first-draft.json --execute --render-timeout 300
python3 -m unittest discover -s tests -v
```

Sin `--execute` solo valida estructura, parámetros y archivos; no conecta a Resolve. Con `--execute` reutiliza el diagnóstico y ejecuta el trabajo en ResolvePython. En este entorno la conexión requiere ejecución fuera del sandbox. No instala dependencias.

El plan de muestra usa el archivo local `prueba.MOV` (no incluido en Git). Sus segmentos 0–5 y 10–15 segundos son una prueba técnica de dos cortes, no una selección editorial basada en el contenido.

## Contrato JSON v1

Ver `plans/first-draft.json`. Campos obligatorios y sin campos desconocidos:

| Campo | Contrato |
| --- | --- |
| `schema_version` | Entero 1 |
| `source` | Un MOV, MP4 o MKV local no vacío; ruta relativa al plan o absoluta |
| `project_prefix` | `AIEditor_Test_` seguido de 1–50 caracteres ASCII alfanuméricos, guion o guion bajo |
| `timeline` | Nombre, ancho y alto pares verticales (alto máximo 3840), FPS entero 24/25/30/50/60 |
| `segments` | 1–100 rangos `{in_seconds, out_seconds}` ordenados según el montaje deseado |
| `output_dir` | Carpeta separada de los originales; relativa al plan o absoluta |

Tiempos relativos al primer frame del archivo, intervalos **[entrada, salida)**. Se convierten al frame más cercano con empate hacia arriba (`Decimal`, half-up). Se rechazan rangos vacíos tras redondeo o fuera de la fuente. Esta versión requiere video vertical con audio y FPS iguales a la timeline; no admite conversión de FPS, ni valores fraccionales. Las superposiciones entre rangos de fuente se permiten: repiten material en el montaje.

Antes de crear la timeline se importan los medios en un **proyecto nuevo de prueba** y se consultan FPS, frames, resolución y canales. Si fallan los metadatos o los rangos, puede quedar un proyecto de prueba vacío o con el medio importado; no se crea la timeline. No se abre ni modifica un proyecto anterior. No se cambia de base de datos ni de carpeta del gestor.

## Ejecución y resultados

Cada ejecución añade fecha/hora del equipo y UUID al nombre del proyecto y crea una subcarpeta exclusiva bajo `output_dir`:

- `plan.json`: entrada resuelta para reproducir el trabajo.
- `result.json`: etapa, versión API, rangos, proyecto, timeline, trabajo de render, errores y tiempo transcurrido.
- `editable.drp`: copia del proyecto editable; requiere conservar el video fuente en su ruta.
- `draft.mp4`: H.264, AAC, 1080 × 1920 a 30 fps para el plan de muestra.

Los clips de video y audio se comprueban por cantidad, posición, duración y offset de origen, junto con la duración y ajustes de timeline. Las pistas adicionales deben estar vacías. La verificación de audio cubre montaje y sincronía de frames; no constituye una escucha ni una comprobación de mezcla perceptual de los seis canales.

El render espera localmente hasta completar o agotar `--render-timeout`. El estado Complete y el archivo no vacío son necesarios para éxito. Ante timeout no cancela trabajos: consultar `render_job` y el proyecto del informe antes de repetir. No hay reanudación automática: repetir crea otro proyecto y otra salida, conservando los anteriores. No hay llamadas de IA dentro del ejecutor. `elapsed_seconds` mide ejecución local; no estima tokens, costo o esfuerzo manual.

## Particularidades verificadas de la instalación

- Usar `ImportMedia([ruta])`; la variante con diccionario `FilePath` no importó este MOV.
- `AppendToTimeline.endFrame` se comporta como límite exclusivo en Studio 21.1.2.10. Usar 150 para 150 frames; con 149 devuelve 149 frames. La comprobación posterior detecta incompatibilidades.
- El MOV expone seis canales de audio. Resolve crea pistas vacías adicionales; solo una contiene los dos clips.
- `ReplaceExistingFilesInPlace: False` fue rechazado aunque está en el stub. La protección contra sobrescritura depende de carpetas exclusivas creadas con `exist_ok=False`, no de ese ajuste.
- ResolvePython no añade la carpeta del script a `sys.path` y puede usar ASCII por defecto. Se fija la ruta de módulos y UTF-8 al leer/escribir planes e informes.

## Límites

Sin subtítulos, efectos, selección automática ni tratamiento de color específico en este hito. La fuente identifica HLG; revisar apariencia y mezcla al calibrar el estilo. El montaje queda abierto en Resolve para revisión humana. Los errores conservan los proyectos y artefactos de prueba para diagnóstico, sin limpiarlos automáticamente. No se prometen reanudación, caché por contenido o portabilidad a otras versiones hasta verificarlas.
