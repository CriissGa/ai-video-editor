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

## Segundo hito: transcripción y muestra de estilo

El usuario confirmó que el primer borrador funcionó y autorizó continuar (2026-11-03). Se respetó su preferencia de usar MCP/API de Resolve; un intento de acceso Computer Use no se aprobó ni llegó a controlar la aplicación.

- Transcripción local nativa persistida: 218 palabras con tiempos de fuente. Segunda llamada devolvió `cached` sin analizar otra vez. Clave por SHA-256 del contenido, versión de Resolve, idioma y configuración.
- Resuelto mediante MCP: desde Deliver, `TranscribeAudio` devolvía False/Inactive. Abrir Edit con la API habilitó la operación; incorporado a la CLI.
- Nuevas herramientas: `transcribe_video.py`, `prepare_captions.py`, `caption_style.py`. Plan v2 con subtítulos relativos a la timeline, énfasis por frase y zoom por segmento; se mantiene v1.
- Propuesta editorial con cuatro segmentos, 695 frames / 23.167 s, 26 subtítulos Text+ editables y zooms 1.0/1.04/1.06/1.10. No es una selección aprobada todavía por el usuario.
- Proyecto final `AIEditor_Test_Editorial_20261103_003001_f7d8b7fa`, timeline `Hair story - style v1`, guardado y abierto. Artefactos en `outputs/editorial/20261103_003001_f7d8b7fa/`: MP4, DRP, SRT, plan, informe y fotogramas.
- Render Complete al 100 %: 9755 ms; ejecución del montaje 15.229 s, sin incluir transcripción/desarrollo. MP4 24 116 043 bytes, 1080 × 1920, 30 fps, H.264/AAC estéreo, metadatos comprobados tras reimportación.
- DRP reimportado como otro proyecto de prueba: cuatro clips online, cuatro composiciones, 26 nodos Text+ y 695 frames conservados.
- Fotogramas de tres segmentos y un fotograma del MP4 revisados: texto legible y debajo del rostro en las muestras. Sin escucha o revisión completa del video.
- Trece pruebas unitarias aprobadas. Transcripción y planes con texto real permanecen excluidos de Git; ejemplo v2 usa textos ficticios. Contratos y uso en `CAPTIONS_WORKFLOW.md`.

## Tercer hito: revisión de texto y acentos

El usuario indicó que le gusta la dirección, pidió texto mayor, borde negro/sombra y señaló que los zooms anteriores apenas se percibían. Confirmó que mezcla español e inglés y que equivocaciones al hablar pueden ser parte del humor; preferencias registradas en AGENTS y D008.

- Preset `bold-yellow-v2`: texto 33 % mayor (0.10), borde negro 0.05 y sombra suave; líneas limitadas a 18 caracteres. El preset anterior se conserva.
- Eventos explícitos reutilizables en `style.events`: tres zooms animados y dos temblores breves elegidos por remate. La selección, palabras y audio se mantuvieron para comparar el estilo.
- Nuevo proyecto separado `AIEditor_Test_Accents_20261103_004452_fe9bfd09`, timeline `Hair story - large captions and accents`, guardado y abierto en Edit. Salidas privadas en `outputs/accents/20261103_004452_fe9bfd09/`.
- 695 frames / 23.167 s, 26 nodos Text+. Render Complete, 9341 ms; ejecución 13.204 s. MP4 de 24 098 876 bytes, vertical 1080 × 1920, 30 fps y AAC estéreo, reimportado y comprobado.
- DRP reabierto con otro nombre de prueba: tamaño/borde/sombra en los 26 textos y expresiones animadas conservados. GetInput confirmó cambio de escala, desplazamiento de temblor y vuelta al centro. Revisados tres fotogramas de acentos y uno del MP4.
- Dieciocho pruebas aprobadas, incluida conservación de palabras mixtas sin normalizar gramática. Transcripción previa reutilizada; reconocimiento bilingüe completo aún pendiente de revisión contra audio.
- Herramienta nueva `scripts/edit_effects.py`; `prepare_captions.py --preset` selecciona el preset y ajusta el ancho de líneas. Contrato y límites en `CAPTIONS_WORKFLOW.md`.

## Límites y pendientes

- Revisar ritmo, exactitud del texto automático, voz y mezcla. El origen identifica HLG y seis canales; no se ha calibrado color ni mezcla perceptual.
- La revisión incluye zooms animados y temblores. Siguen pendientes animación palabra por palabra, sonidos, blur y transiciones; intensidad final sujeta a revisión del usuario.
- Los subtítulos son nodos Fusion, no una pista nativa de subtítulos. DRP requiere conservar el original.
- FPS enteros iguales entre fuente y timeline. Sin reanudación automática de montaje; repetir crea nuevo proyecto/salida. La transcripción sí permite reutilizar caché o continuar un proyecto de transcripción de prueba.
- No se han medido tokens, costos ni esfuerzo manual. Notion documenta hitos mediante el agente, sin sincronización automática.

## Siguiente paso

Revisar `outputs/accents/20261103_004452_fe9bfd09/draft.mp4` y ajustar tamaño/sombra e intensidad de los acentos según comentarios. Después revisar pasajes mixtos español/inglés contra el audio sin borrar sus equivocaciones cómicas; añadir sonidos solo cuando apoyen un remate.

## Dirección creativa confirmada

Video vertical, cámara estática y usuario a cámara. Humor rápido inspirado en Rubius y HolaSoyGerman con identidad propia: subtítulos llamativos con color selectivo, frases destacadas, zooms, temblores, blur, transiciones y sonidos según el remate. Mantener rostro visible, voz clara y pausas cómicas. Retención como objetivo a medir.
