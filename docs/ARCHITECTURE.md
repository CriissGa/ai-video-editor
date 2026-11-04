# Arquitectura

## Dirección aceptada

Un conjunto de herramientas locales operado por un agente, con DaVinci Resolve Studio como motor de edición. El proyecto debe poder usarse desde distintos agentes sin depender del historial de un chat.

## Componentes

| Componente | Responsabilidad |
| --- | --- |
| Agente | Interpretar instrucciones, consultar material relevante y proponer decisiones editoriales |
| Plan de edición | Persistir fuentes, segmentos, tiempos, textos, estilo y destino de salida |
| Herramientas locales en Python | Validar entradas, ejecutar etapas, reutilizar resultados y registrar estado |
| Adaptador de Resolve | Traducir operaciones a la API de la instalación disponible |
| Archivos del trabajo | Conservar planes, transcripciones, resultados y versiones |
| Notion | Documentar alcance, decisiones e hitos |

## Flujo

1. Inspeccionar el material y guardar metadatos.
2. Transcribir cuando sea necesario y conservar tiempos referidos a la fuente.
3. Definir un plan de edición con intervención del usuario o del agente.
4. Validar el plan antes de ejecutar cambios.
5. Crear una timeline de trabajo en Resolve y comprobar el resultado.
6. Aplicar subtítulos y estilo dentro de las capacidades verificadas.
7. Exportar un borrador y registrar el resultado para revisión humana.

El flujo debe permitir repetir una exportación sin volver a pedir decisiones al modelo.

## Contratos y evolución

- Python para herramientas locales y JSON para planes de edición.
- Comandos locales como primera interfaz; MCP propio solo si facilita su uso después.
- MCP de Resolve existente para explorar capacidades y realizar pruebas de integración.
- Plan y resultados persistidos para continuar un trabajo desde otro agente.
- Validación de versión del plan, fuentes y rangos antes de ejecutar.
- Convención de tiempos y conversión a frames definida para v1 en `EDIT_WORKFLOW.md`.
- Registro de etapas completadas y artefactos producidos; reanudación sin duplicaciones pendiente.
- Evolución pendiente: caché vinculada al contenido y parámetros con invalidación.

Herramientas implementadas: `scripts/diagnose_resolve.py` verifica conectividad de lectura mediante ResolvePython y subproceso con tiempo límite. `scripts/edit_video.py` valida el plan local, reutiliza el diagnóstico y ejecuta importación, montaje, comprobaciones y render con código local, sin IA por operación. El mismo módulo contiene el adaptador mínimo de Resolve para evitar capas prematuras.

Contrato v1 y resultados en `EDIT_WORKFLOW.md`: una fuente vertical con audio, FPS enteros iguales, rangos [entrada, salida) redondeados half-up a frames. El plan reside en `plans/`; medios y resultados privados en rutas locales excluidas de Git. Cada ejecución conserva plan resuelto, informe de etapas, copia DRP y MP4 en una carpeta exclusiva. Se comprueban fuente y rangos antes de crear timeline, y clips de video/audio antes de renderizar. No hay reanudación automática del montaje; repetir crea otra ejecución aislada. La caché de transcripción sí está implementada por contenido y configuración.

## Primer alcance propuesto

Un archivo hablado, un segmento indicado por tiempos, timeline vertical de 1080 × 1920, subtítulos sencillos y exportación de borrador. Mantener la timeline editable.

## Límites iniciales

- Sin aplicación gráfica, servidor permanente ni base de datos al inicio.
- Sin publicación automática en redes sociales.
- Selección inteligente, subtítulos animados, reencuadre automático y B-roll sujetos a validación posterior.
- No prometer paridad entre la interfaz de Resolve y su API.
- La conexión con Notion es documental mediante el agente; no hay sincronización en segundo plano.

## Verificación pendiente

Versión y acceso de scripting confirmados con Studio 21.1.2.10 (ver `RESOLVE_DIAGNOSTIC.md`). Importación, montaje por rangos, timeline editable, DRP y render MP4 verificados en Studio 21.1.2.10 con dos cortes y 300 frames. Subtítulos Text+ editables y zooms verificados en una muestra editorial de 695 frames. Pendiente: revisión perceptual de color/mezcla, calibración editorial y efectos adicionales. Después probar tres videos representativos y medir correcciones manuales, tiempo de proceso y consumo de IA.

## Dirección creativa y eventos de edición

Entrada confirmada: videos verticales con cámara estática y el usuario a cámara. Montaje cómico rápido inspirado en recursos de Rubius y HolaSoyGerman, con identidad propia moderna. Recursos: subtítulos con color selectivo, frases destacadas, zooms, temblores, blur, transiciones y efectos sonoros.

El plan deberá describir eventos con tiempo, duración, intensidad y referencias a presets y sonidos reutilizables. Validar cada recurso en Resolve. Preservar rostro, legibilidad, voz y pausas cómicas. Evaluar seguimiento facial según el movimiento real: cámara estática no significa rostro inmóvil.


## Transcripción y estilo implementados

`scripts/transcribe_video.py` genera transcripción nativa de Resolve y caché SHA-256 con versión/configuración en `transcripts/`. Normaliza palabras a frames de fuente. `scripts/prepare_captions.py` valida la identidad del contenido y proyecta las palabras al montaje seleccionado por el agente, generando un plan v2 privado. No selecciona fragmentos automáticamente.

`scripts/caption_style.py` valida subtítulos en tiempo de timeline y aplica el preset Text+ con énfasis por frase y Transform para zooms; exporta SRT y fotogramas. `edit_video.py` mantiene compatibilidad v1 y añade la etapa de estilo antes de guardar DRP y renderizar v2. Contratos y evidencia en `CAPTIONS_WORKFLOW.md`. Los nodos siguen editables al reimportar DRP. No existe pista nativa de subtítulos ni animación palabra por palabra todavía.


`scripts/edit_effects.py` valida eventos opcionales `style.events` en el plan v2 y genera expresiones de escala/posición para el Transform del video. Tipos actuales: `punch_zoom` y `shake`, con tiempo e intensidad limitados y sin solapamientos del mismo tipo. La escala base del segmento se conserva; los acentos son multiplicadores temporales. `caption_style.py` comprueba muestras reales de animación con GetInput y registra los valores en el informe. El preset anterior permanece disponible; `bold-yellow-v2` aumenta tamaño/borde y añade sombra.


## Sonidos y ruta MCP

`prepare_sounds.py` cataloga medios de `sonidos/` y conserva copias PCM cacheadas, sin modificar originales. `sound_edit.py` valida recortes, posiciones, ganancias y fundidos, importa medios y monta una pista SFX separada. El plan v2 admite `audio` opcional. `edit_video.export_draft` se comparte entre ejecución normal y recuperación mediante MCP.

La integración nativa con SFX produjo dos fallos Qt de Resolve y quedó bloqueada en la CLI. Validar sigue disponible; montaje/exportación con sonidos se completaron mediante funciones locales invocadas desde MCP en etapas separadas. No se considera estable ni probada la ruta nativa completa de audio. Los presets sin audio conservan su CLI; los workers tienen timeout externo para no quedar esperando indefinidamente si se pierde Resolve. Contrato y evidencia en `SOUND_WORKFLOW.md`.


## Historia multi-fuente y gestión de color

`story_plan.py` añade validación v3 por fuentes identificadas y montaje/verificación de identidad, tiempos y parámetros. Reutiliza validadores v2, `source_ranges` y comprobaciones del ejecutor. `caption_style.apply_style` trabaja por rangos de clips para guardar lotes y añade zoom progresivo con keyframes reales; los acentos quedan en un Transform separado. `color_pipeline.py` configura/verifica el perfil HLG→SDR y adapta solo la luminancia de los gráficos Text+ bajo esa configuración.

La exportación puede iniciar de forma no bloqueante, persistiendo el ID antes de consultar su terminación. Validación CLI sigue disponible; v3 y audio se operan por etapas MCP. Después de otro cierre de AddTrack incluso por MCP, `sound_edit` deja de crear pistas y exige una vacía compatible; `prepare_sounds --channels 1` permite usar pistas mono existentes. La alternativa se verificó en la pieza completa, sin considerar resuelta la causa interna de Qt. Contratos y evidencia en `FULL_STORY_WORKFLOW.md`.


La revisión corta incorpora `caption_animation.py` para tamaño adaptativo y entradas cinéticas, eventos `whip` con pan/blur y perfil SDR suave separado. El audio mono se observó silencioso al exportar aislado: las comprobaciones de clips/ganancias no garantizan ruteo al bus. Ese límite está abierto y debe comprobarse por archivo exportado.


`revise_workspace.py` modifica las composiciones existentes de una sola timeline propia, sin crear proyectos/pistas ni renderizar: zoom de dos keyframes con pivote facial manual, anulación de desplazamientos de acento y variantes de entrada Text+. La revisión usa parámetros persistidos privadamente en `outputs/workspace/revision-plan.json`; no incorpora seguimiento facial. Respaldos DRP y manifiesto de limpieza son artefactos locales privados.


`timeline_titles.py` separa los Text+ en V2 mediante una semilla nativa y adaptación DRT limitada a Studio 21.1.2.10. Exige una base con dos pistas nativas de cada tipo; conserva sus IDs, metadatos de registro y buses, reemplazando solo los clips de V2. Crear pistas copiando nodos XML no basta para que compongan/salgan al bus y se descarta. La base provino de importación XML de Resolve; la adaptación del DRT es específica de versión, no un contrato público estable. `style_titles` configura texto/estilo/entradas sin incrustarlos en cámara. Verificar fotograma compuesto, enlaces de audio y salida real además de conteos.


`tighten_plan.py` cruza niveles RMS por frame de PCM mono con palabras cacheadas para recortar solo silencios no protegidos; persiste tramos/resultados y conserva márgenes. `rebuild_timing.py` actualiza clips de una primera fuente en DRT propio, manteniendo referencias de medios y registro nativo V1/V2/A1/A2; no crea pistas. Tras importar se comprueban offsets/duraciones y se aplican composiciones de cámara por lotes. El plan privado de revisión añade `face` por segmento y `caption_emphasis`; no son todavía campos del validador general v1/v2/v3. Los efectos que atraviesan un corte usan tiempos negativos entre paréntesis para no generar comentarios Lua.


`update_motion.py` modifica keyframes, pivotes y expresiones en composiciones existentes, validando proyecto, timeline única, rangos y nodos antes de cambiar. Reutiliza zoom/acento y añade Blur solo si falta: no reconstruye montaje, títulos o pistas. Intensidades, tiempos y sonidos adicionales se mantienen en el plan privado de cada revisión. Se comprobó una actualización de los 17 planos en dos lotes y doce SFX añadidos a la pista existente.
