# Transcripción y primera muestra de estilo

## Uso

Con Resolve Studio abierto, desde la raíz del repositorio:

```sh
python3 scripts/transcribe_video.py prueba.MOV
```

Devuelve la ruta de un JSON privado en `transcripts/`. Usa transcripción nativa local, sin servicios externos ni paquetes nuevos. La clave de caché incluye SHA-256 del archivo completo, versión de Resolve, idioma solicitado y detección de hablantes. Una segunda llamada con el mismo contenido/configuración devuelve `cached` sin iniciar análisis. Solo se verificó `--language auto`; se detectó inglés en esta muestra.

El JSON conserva la respuesta original de Resolve y palabras normalizadas a frames relativos al inicio del archivo, descontando `Start TC`. Esta versión admite timecode con FPS entero y sin drop-frame. Las transcripciones automáticas necesitan revisión: las frases mixtas y nombres pueden contener errores.

Para proyectar las palabras de una transcripción a los segmentos de un plan v1:

```sh
python3 scripts/prepare_captions.py RUTA_PLAN_V1 RUTA_TRANSCRIPCION outputs/mi-plan-v2.json --zooms 1 1.04
python3 scripts/edit_video.py outputs/mi-plan-v2.json
python3 scripts/edit_video.py outputs/mi-plan-v2.json --execute
```

Usar un zoom por segmento; si se omiten todos, usa 1.0. El preparador verifica el hash del contenido contra la transcripción, conserva el orden de montaje y crea el plan de salida solo si no existe. No elige segmentos: esa decisión editorial se persiste en el plan v1. Agrupa hasta cuatro palabras, dos líneas, pausas y finales de frase; la agrupación es inicial y puede corregirse en el JSON.

`plans/style-example.json` documenta el esquema v2 con textos ficticios: sirve para probar el preset, no representa lo que dice el video. Los planes reales con texto del usuario deben guardarse en `outputs/` u otra carpeta privada excluida de Git.

## Plan v2 y preset

Conserva los campos v1 y añade:

- `zoom` obligatorio por segmento, de 1 a 1.2.
- `style: {"preset": "bold-yellow-v1"}`.
- `captions`: lista ordenada de `{in_seconds, out_seconds, text, emphasis}`. Los tiempos se refieren a la **timeline resultante**, no a la fuente, con intervalos [entrada, salida) y redondeo half-up a frames. Sin solapamientos ni rangos fuera del montaje; máximo 500 subtítulos, dos líneas de 24 caracteres y 44 caracteres totales.

El preset usa Arial Bold, tamaño Fusion 0.075, centro normalizado (0.5, 0.25), texto blanco, énfasis amarillo y contorno negro. El énfasis aplica a una frase completa: no hay resaltado animado palabra por palabra todavía. El preparador marca algunas frases en inglés; el plan permite corregir `emphasis` manualmente para cualquier idioma.

Cada clip contiene una composición Fusion con MediaIn, Transform (zoom del video), Text+ y Merge temporizados, y MediaOut. Los subtítulos permanecen como nodos editables en el proyecto/DRP; se integran en la imagen del MP4. No crea una pista nativa de subtítulos. También exporta `captions.srt` sin formato y un fotograma por segmento para revisión. Un subtítulo que cruza un corte se representa en ambas composiciones recortado al rango correspondiente.

El ejecutor comprueba texto aplicado, zoom, encendido/apagado de cada subtítulo en sus límites y mantiene las comprobaciones de cortes de video/audio. Guarda y exporta el DRP después de aplicar el estilo.

## Particularidades comprobadas mediante MCP/API

`TranscribeAudio` devolvía False y estado Inactive desde Deliver. `resolve.OpenPage('edit')` habilitó el análisis en Studio 21.1.2.10; la herramienta ahora lo realiza automáticamente. La obtención de transcripción, prueba de Fusion y verificación del DRP se hicieron mediante MCP/API, sin controlar la interfaz con Computer Use.

`--project AIEditor_Test_Transcript_…` permite continuar la espera o extraer una transcripción existente de un proyecto de prueba del mismo medio e idioma. No admite proyectos con otro prefijo. El tiempo guardado mide la ejecución de esa invocación; si el análisis ya estaba completo, **no representa la duración total del análisis original**. En timeout se conserva el proyecto; comprobarlo antes de repetir.

## Muestra editorial verificada

2026-11-03, America/Phoenix: el usuario confirmó que el borrador técnico funcionó y autorizó continuar. Se eligieron cuatro segmentos del video local, conservando el idioma original, para presentar un cambio de cabello, la intención de verse profesional, el primer intento por hacerlo solo y el remate del trabajo para clase. Es una propuesta de edición del agente pendiente de revisión humana.

Transcripción persistida: 218 palabras. Caché reutilizada sin nuevo análisis. Montaje: 695 frames / 23.167 s a 30 fps, cuatro clips, 26 subtítulos y zooms 1.0/1.04/1.06/1.10. Render Complete: 9755 ms; ejecución de edición 15.229 s (no incluye desarrollo ni transcripción). MP4 de 24 116 043 bytes, H.264/AAC estéreo, vertical 1080 × 1920, reimportado para comprobar metadatos y un fotograma renderizado.

Proyecto final `AIEditor_Test_Editorial_20261103_003001_f7d8b7fa`, dejado abierto. Carpeta privada `outputs/editorial/20261103_003001_f7d8b7fa/`. DRP importado con otro nombre de prueba: cuatro clips online, cuatro composiciones, 26 nodos Text+ y 695 frames conservados. Se revisaron fotogramas del montaje y del MP4: legibilidad, contorno y ubicación debajo del rostro en las muestras inspeccionadas. Esto no sustituye revisar todos los movimientos y escuchar el audio.

Sin temblores, blur, sonidos o transiciones añadidos en este preset. La mezcla perceptual, color HLG, ritmo y exactitud de transcripción requieren revisión del usuario. La primera muestra sirve para decidir esos ajustes.


## Revisión: texto grande, sombra y acentos animados

El usuario pidió texto más grande, borde negro, algo de sombra y efectos más visibles. `bold-yellow-v2` conserva el texto blanco/amarillo y usa tamaño 0.10 (33 % mayor que v1), contorno negro 0.05 y tercera capa de sombreado negra, alpha 0.5, desplazamiento (0.025, -0.025) y suavidad 0.012. Máximo 18 caracteres por línea para evitar recortes. `bold-yellow-v1` conserva sus parámetros anteriores.

```sh
python3 scripts/prepare_captions.py RUTA_PLAN_V1 RUTA_TRANSCRIPCION outputs/plan-grande.json --preset bold-yellow-v2
```

El plan v2 acepta `style.events` opcional. Cada evento tiene `type`, `in_seconds`, `out_seconds`, `amount`; los tiempos se refieren al montaje final, como los subtítulos:

| Tipo | Intensidad y duración |
| --- | --- |
| `punch_zoom` | Multiplicador 1.05–1.35, entre 4 frames y 3 s |
| `shake` | Desplazamiento normalizado horizontal 0.001–0.015, entre 3 frames y 0.6 s; vertical al 65 % |

Máximo 40 eventos, dentro de la timeline y sin solapamiento del mismo tipo. Zoom y temblor sí pueden coincidir. Los eventos se intersectan con cada clip conservando el tiempo de timeline. Entrada en 3 frames y salida en 4; el temblor añade sobreescaneo del 4 % para proteger los bordes. Su escala se multiplica por la del segmento y por el zoom activo. Los textos se componen después del Transform y permanecen estables.

`plans/style-example.json` incluye ambos efectos con textos ficticios. El informe conserva muestras de escala/centro evaluadas por Resolve durante cada evento. Pruebas cubren límites, reset al finalizar, traslación a tiempo local y conservación de una frase mixta sin corregir gramática.

Nueva muestra: `outputs/accents/20261103_004452_fe9bfd09/`, proyecto `AIEditor_Test_Accents_20261103_004452_fe9bfd09`. Misma selección y audio que la muestra anterior (695 frames, 23.167 s), 26 subtítulos, tres acentos de zoom y dos temblores. Render Complete: 9341 ms; ejecución 13.204 s. MP4 24 098 876 bytes, 1080 × 1920, 30 fps y AAC estéreo, comprobado tras reimportar. DRP reabierto en proyecto separado: tamaño/borde/sombra en los 26 nodos y expresiones de zoom/temblor conservados. Revisados fotogramas en tres acentos y un fotograma del MP4; pendiente revisión humana del movimiento completo y del audio. Dieciocho pruebas aprobadas.

### Política de idioma confirmada

Preservar español, inglés, cambios de idioma, acento y equivocaciones reales al hablar. La herramienta proyecta palabras sin traducir ni corregir gramática. No confundir errores del reconocimiento con errores hablados: los primeros requieren contraste con el audio; los segundos pueden ser parte del chiste. El detector de idioma principal no garantiza fidelidad en pasajes mixtos. En esta revisión se reutilizó la transcripción previa; no se certificó una nueva transcripción bilingüe ni se modificó el audio.
