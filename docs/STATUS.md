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

## Cuarto hito: palabras de foco y sonidos

El usuario pidió una edición más alegre/exagerada, palabras importantes mayores y bordes más gruesos, y aportó siete archivos en `sonidos/`.

- Preset `bold-party-v3`: texto normal 0.105, palabras de foco 0.14 con pop inicial de seis frames, borde negro 0.075 y sombra. El preparador separa palabras de foco en español/inglés sin corregir gramática. Presets previos disponibles.
- Catálogo local de siete sonidos: copias PCM16 estéreo/48 kHz cacheadas por SHA-256, duraciones/picos y regiones activas. No hubo servicios externos ni dependencias nuevas; `afconvert` funcionó fuera del sandbox.
- Se produjeron **dos cierres de Studio 21.1.2.10** durante el flujo nativo con importación de sonidos, con assertion Qt `QList::insert`. No se identificó causa única. El segundo dejó worker esperando; se terminó solo ese worker. El usuario cerró el aviso de reporte y reabrió Resolve.
- Recuperación verificada mediante llamadas MCP separadas sobre el proyecto de prueba guardado. La CLI valida planes con audio pero bloquea su ejecución nativa antes de conectar; no repetir esos lotes. Las funciones de audio y exportación se usan desde MCP. Detalle en `SOUND_WORKFLOW.md`.
- Proyecto final `AIEditor_Test_Playful_20261103_010423_81a230c0`, timeline `Hair story - playful words and SFX`, guardado y abierto en Edit. Artefactos en `outputs/playful/mcp_20261103_011224_b0cb313c/`.
- 695 frames / 23.167 s, 35 textos, tres zooms/dos temblores algo más intensos y cinco SFX en pista A6. Cuatro archivos distintos usados; ganancias -20/-18 dB con fundidos 1/2 frames, voz -3 dB.
- Render Complete: 10292 ms; exportación medida 11.842 s (sin incluir fallos, montaje o desarrollo). MP4 24 094 690 bytes, 1080 × 1920/30 fps/AAC estéreo, reimportado y comprobado. Pico PCM decodificado -2.93 dBFS (no true peak); sin revisión auditiva completa.
- DRP reabierto en proyecto separado: 35 textos con borde 0.075 y cinco SFX online conservados. Fotogramas de tres palabras importantes revisados.
- Veinticuatro pruebas aprobadas, incluida la guardia que impide ejecutar audio por la ruta nativa. Medios originales, copias PCM, transcripción y planes reales siguen fuera de Git.

## Quinto hito: historia completa, zoom gradual y HLG→SDR

El usuario añadió `pruebapart2.MOV`, pidió más volumen de SFX, zoom progresivo con keyframes y revisar la diferencia de color al exportar. La duración final solicitada para esta pieza es 2–2½ minutos.

- Segunda fuente verificada: 43929 frames / 24:24:09, vertical 1080 × 1920/30 fps, seis canales y Rec.2100 HLG/H.265 10-bit, igual perfil HLG que la primera. Transcripción nativa de 775 palabras persistida; primera transcripción reutilizada.
- Plan v3 multi-fuente implementado y validado, con identidad de fuente por clip. Historia seleccionada: 3659 frames / **2:01.967**, 21 clips, 121 textos y 14 zooms progresivos con keyframes BezierSpline comprobados por valores inicial/intermedio/final. Los acentos rápidos están en un Transform separado.
- Color base mediante RCM v2: entradas HLG, timeline DaVinci WG/Intermediate, salida Rec.709 Gamma 2.4 con DRT DaVinci y 100 nits. Compensación gráfica verificada de los textos para conservar blanco/amarillo; no se cambia la imagen de cámara con esa compensación. Es base técnica, no look creativo final ni garantía de coincidencia entre todos los reproductores.
- Nuevo cierre por MCP en AddTrack tras Fusion, 2026-11-03 01:39:55 del equipo. No se perdió el montaje guardado. El usuario reabrió Resolve. Se eliminó AddTrack del adaptador de SFX: se reutilizó A2 mono vacía con copias mono, manteniendo las cinco pistas existentes. La causa Qt no está resuelta; la CLI con audio sigue bloqueada.
- Nueve SFX a -14/-12 dB, **+6 dB** respecto a la muestra previa; voz -3 dB, fundidos 1/2 frames. Salida AAC estéreo. Efectos mono en esta versión para usar la pista existente.
- Proyecto final `AIEditor_Test_FullStory_20261103_013802_ff358b40`, timeline `Hair story - complete HLG to SDR`, guardado y abierto en Edit. Artefactos finales en `outputs/full-story/20261103_013802_ff358b40/final/`: MP4, DRP, plan, informe, SRT y fotograma renderizado.
- Render final Complete al 100 %, 66447 ms; MP4 **126 893 818 bytes**, 1080 × 1920/30 fps/H.264/AAC estéreo. Reimportado: 3659 frames, entrada identificada como **Rec.709 Gamma 2.4**, gamma 2.4. Audio PCM decodificado 122.004 s por relleno AAC, pico de muestra **-2.89 dBFS**, no true peak.
- DRP reabierto como otro proyecto de prueba: 21 clips, 121 nodos Text+, nueve SFX online, keyframes y configuración RCM conservados. Se revisaron cinco fotogramas de timeline, blanco/amarillo y un fotograma del MP4 final. No se escuchó ni se revisó cada frame del video completo.
- Treinta pruebas aprobadas. Documentación del contrato y recuperación en `FULL_STORY_WORKFLOW.md`; ejemplos sin texto privado. El render anterior con gráficos apagados se conservó en la carpeta padre y **no es la entrega final**.

## Límites y pendientes

- Revisar ritmo, exactitud del texto automático, voz y mezcla perceptual. HLG→SDR y etiquetas verificados; look creativo, exposición fina y comparación en el dispositivo del usuario aún requieren revisión.
- La revisión incluye zooms/temblores, pop de palabras importantes y SFX. Siguen pendientes resaltado continuo palabra por palabra, blur y transiciones visuales; mezcla e intensidad final sujetas a revisión del usuario.
- Los subtítulos son nodos Fusion, no una pista nativa de subtítulos. DRP requiere conservar el original.
- FPS enteros iguales entre fuentes y timeline. Montaje v3 por etapas MCP, con guardado por lotes; no hay reanudación automática que rehaga composiciones. La transcripción permite reutilizar caché.
- No se han medido tokens, costos ni esfuerzo manual. Notion documenta hitos mediante el agente, sin sincronización automática.

## Siguiente paso

Revisar `outputs/full-story/20261103_013802_ff358b40/final/draft.mp4` completo en el dispositivo del usuario: ritmo, balance SFX/voz, subtítulos y color SDR. Afinar look y cortes con sus comentarios. Mantener SFX en pistas vacías compatibles y no usar AddTrack sobre Fusion cargado; diagnosticar ese fallo en un hito separado.

## Dirección creativa confirmada

Video vertical, cámara estática y usuario a cámara. Humor rápido inspirado en Rubius y HolaSoyGerman con identidad propia: subtítulos llamativos con color selectivo, frases destacadas, zooms, temblores, blur, transiciones y sonidos según el remate. Mantener rostro visible, voz clara y pausas cómicas. Retención como objetivo a medir.
