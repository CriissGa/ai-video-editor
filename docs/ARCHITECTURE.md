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
