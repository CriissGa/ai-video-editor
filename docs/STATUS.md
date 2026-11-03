# Estado del proyecto

## Situación actual

Primer flujo completo implementado y verificado el 2026-11-03 (America/Phoenix), con DaVinci Resolve Studio 21.1.2.10. Herramientas locales Python sin dependencias externas: diagnóstico y ejecutor de planes JSON. Repositorio privado: https://github.com/CriissGa/ai-video-editor.

## Hito verificado

- `scripts/edit_video.py` valida JSON, archivos y parámetros; reutiliza el diagnóstico existente y ejecuta con ResolvePython 3.14.4 fuera del sandbox.
- Plan `plans/first-draft.json`: fuente local `prueba.MOV`, cortes 0–5 s y 10–15 s. Selección técnica para validar el montaje, sin criterio editorial aplicado todavía.
- Fuente: vertical 1080 × 1920, 30 fps, 3635 frames y seis canales de audio. Solo metadatos técnicos mínimos en los informes.
- Proyecto separado final: `AIEditor_Test_FirstDraft_20261103_001812_b2c4b70c`, timeline `Primer borrador`, guardado y dejado abierto. No se editaron proyectos originales.
- Verificados posiciones, offsets y duración de los dos clips en video y audio: 300 frames, 10 segundos. Pistas extra vacías.
- Render Complete, 100 %, 2607 ms informados por Resolve; ejecución del flujo 5.367 s. No incluye desarrollo, revisiones o pruebas fallidas; no representa ahorro ni costo de IA.
- Artefactos locales: `outputs/first-draft/20261103_001812_b2c4b70c/`: `draft.mp4` (10 400 034 bytes), `editable.drp`, `plan.json` y `result.json`.
- MP4 reimportado en otro proyecto de prueba y metadatos comprobados: H.264, AAC estéreo, 1080 × 1920, 30 fps, 300 frames y duración 00:00:10:00. Después se volvió a abrir el proyecto final.
- Siete pruebas unitarias aprobadas (diagnóstico, validación, conversión de tiempos y detección de cortes incorrectos).
- Proyectos y artefactos de intentos fallidos conservados para diagnóstico; no se eliminan automáticamente. Detalles de compatibilidad en `EDIT_WORKFLOW.md`.

## Límites y pendientes

- Falta revisión humana de imagen, voz y mezcla. El origen identifica HLG y tiene seis canales; no se ha calibrado color ni mezcla perceptual.
- Sin subtítulos, efectos ni selección automática en este hito. La copia DRP requiere el video original en su ruta.
- Esta versión requiere una fuente vertical con audio y FPS enteros iguales a la timeline. No hay reanudación automática; repetir crea nuevo proyecto y salida.
- No se han medido tokens, costos ni esfuerzo manual. Sin servidor o interfaz propios.
- Notion actualizado con el estado y el hito verificado; documenta mediante el agente, sin sincronización automática. README contiene su enlace.

## Siguiente paso

Revisar el borrador técnico y elegir un fragmento con sentido editorial. Después validar subtítulos sencillos y un preset reutilizable de estilo en una nueva timeline de prueba, incluyendo revisión de color HLG y mezcla estéreo.

## Dirección creativa confirmada

Video vertical, cámara estática y usuario a cámara. Humor rápido inspirado en Rubius y HolaSoyGerman con identidad propia: subtítulos llamativos con color selectivo, frases destacadas, zooms, temblores, blur, transiciones y sonidos según el remate. Mantener rostro visible, voz clara y pausas cómicas. Retención como objetivo a medir.
