# Estado del proyecto

## Revisión vigente — énfasis semántico y encuadres variados (2026-11-03)

Mismo proyecto y única timeline de 63.733 s. Los 124 elementos de V2 son títulos Text+ nativos editables en Inspector, no pista nativa de subtítulos. Se ampliaron los énfasis de diez a 28: 15.433 s / **24.22 % del tiempo total** (aproximación al 25 % pedido). Cinco variantes de entrada; amarillo para focos, cian para idioma/acento y rosa para determinados remates. Selección semántica persistida en `outputs/workspace/caption-focus-plan.json`; no traducción ni normalización de lo hablado.

Los 17 planos alternan escala de arranque y conservan progresivos hacia pivotes faciales manuales, 17 acentos de zoom, ocho shakes y 12 barridos. Se mantuvieron los 26 SFX y las pistas habilitadas. Verificados tres fotogramas compuestos: texto legible sin cortar el rostro en esas muestras; no seguimiento automático ni revisión de todos los frames. Sin nuevo proyecto/timeline, render completo, AddTrack o cierre observado. Copias DRP antes/después (`before-caption-focus.drp`, `caption-focus-editable.drp`). 34 pruebas aprobadas.

**Próximo paso:** reproducir la timeline para valorar las cinco entradas, cobertura del énfasis y continuidad de encuadres; revisar los errores pendientes del reconocimiento bilingüe contra el audio.

## Revisión vigente — más acercamientos, barridos y sonidos (2026-11-03)

El usuario pidió aumentar movimiento y sonidos en esta última edición. Se actualizó la **misma timeline**, sin cambiar sus cortes ni sus 63.733 s: 17 planos, 124 Text+ independientes, V1/V2 y A1/A2. Plan privado `outputs/workspace/extra-motion-plan.json`; respaldo antes y después (`before-extra-motion.drp`, `extra-motion-editable.drp`).

- Progresivos con escalas iniciales/finales variables hasta 1.24, **17 acentos de zoom** (antes 10), **ocho temblores** (antes seis) y **12 barridos** (antes seis). Pivotes manuales por plano; se corrigió el sentido de un barrido y su pivote al revisar el encuadre. Se revisaron seis muestras de cámara y dos compuestas; rostro/rasgos visibles en esas muestras, sin afirmar tracking facial ni revisar todos los frames. Los acercamientos extremos pueden cortar cabello por arriba.
- **26 SFX online** en A2 (antes 14): doce acentos breves añadidos sin superponer clips, ganancias -7 dB y fundidos de un frame. Se conservaron los sonidos anteriores, los títulos y la voz. Muestra aislada de tres segundos con nuevos sonidos exportada Complete; pico de muestra PCM -11.98 dBFS y 34386 muestras no nulas. No es true peak ni escucha completa de la mezcla. Voz y SFX restablecidos/habilitados y configuración de render devuelta a pieza completa/1080×1920.
- Verificados por API escalas inicial/intermedia/final en los 17 planos, expresiones evaluables, posiciones/ganancias/enlaces de los 26 sonidos, una timeline y dos pistas por tipo. 33 pruebas aprobadas. Sin cierres observados ni AddTrack; no se creó proyecto/timeline ni render completo.

**Próximo paso:** reproducir esta revisión directamente en Resolve para valorar si los acercamientos y sonidos ya tienen la fuerza deseada; ajustar momentos concretos. Estos valores corresponden a esta revisión, no son una cadencia obligatoria para todos los videos futuros.

## Revisión vigente — movimiento y cortes más agresivos (2026-11-03)

El usuario renovó la petición de aplicar zooms/temblores después de la pregunta informada sobre el riesgo. Se probó primero un clip con respaldo; funcionó. No hubo nuevos cierres observados en esta revisión. Proyecto `AI Editor - Prueba 1`, **una sola timeline** `Prueba 1 - Edicion principal`, 1912 frames / **63.733 s**, 17 planos. Respaldo anterior y final en `outputs/workspace/` (`before-punchier.drp`, final `punchier-safe-text.drp`).

- Silencios analizados en PCM16 mono local a 48 kHz, umbral -38 dBFS RMS por frame y protección de palabras con dos frames de margen; se quitaron 134 frames / 4.467 s respecto al montaje de 68.2 s. Conserva voz/revisión de cortes pendiente de escucha completa; no es detección perfecta ni eliminación de toda pausa cómica. Plan/registro privados en `punchier-plan.json`.
- **Aplicados y guardados:** acercamiento progresivo 1.0→1.10/1.16 en los 17 clips, con pivote facial manual; diez punch zooms de 16–22 %, seis shakes de nueve frames y seis barridos de cinco frames con desplazamiento, sobreescaneo y blur. Los textos quedan estables sobre los efectos de imagen. No es tracking facial automático ni un plugin nativo de transición entre dos clips.
- **124 Text+ independientes en V2**, diez énfasis con tres animaciones más fuertes alternadas: pop con overshoot, deslizamiento lateral y entrada desde arriba. Tamaño de foco hasta 0.175, ajustado para palabras largas, contorno 0.09. Saludo español confirmado conservado. Catorce SFX online en A2 reubicados con los cortes, voz A1 y SFX habilitados. No se repitió la mezcla perceptual completa ni render final; la prueba sonora del hito anterior sigue como evidencia de ruteo, no aprobación de la mezcla actual.
- Verificados por API: duración/offset de cada plano, zoom inicial/intermedio/final, conexión MediaOut, composición en los 17 clips y tiempos de títulos. Revisados cuatro fotogramas de encuadre y tres compuestos (dos énfasis y un barrido), sin recortes de rostro/texto en esas muestras. Falta reproducción completa en tiempo real para juzgar intensidad/ritmo.
- Un efecto que cruzaba un corte generaba `time--17`, interpretado como comentario Lua; se corrigió con paréntesis en las coordenadas temporales y se reparó el clip parcial, sin crash. Prueba de regresión incluida. 33 pruebas aprobadas. No se llamó AddTrack ni se creó un proyecto nuevo. Se eliminó la única timeline anterior tras respaldo; la vigente contiene los efectos, no es la revisión previa sin zoom.

**Siguiente paso:** reproducir esta timeline completa en Resolve y ajustar con comentarios concretos sobre cortes, intensidad del zoom/temblor y lectura. Revisar reconocimiento bilingüe restante contra audio; no traducir ni corregir lo realmente hablado.

## Revisión vigente — títulos en timeline y SFX comprobados (2026-11-03)

Proyecto `AI Editor - Prueba 1`, una sola timeline `Prueba 1 - Edicion principal`: montaje de toda la primera fuente hablada, 68.2 s / 2046 frames y 15 clips; recorta esperas largas, incluida la salida de cámara. No incluye parte 2. V1 imagen, V2 **122 clips Text+ nativos independientes**, A1 voz mono y A2 **14 SFX mono online** de los siete sonidos aportados. Tres variantes de entrada, diez títulos destacados más grandes, contorno grueso/sombra. El saludo español fue confirmado por el usuario; transcripción española adicional cacheada localmente. El resto del reconocimiento bilingüe sigue pendiente de revisión contra la voz, sin traducirlo ni declarar exactitud total.

- Títulos visibles sobre imagen comprobados en fotograma compuesto y editables en Inspector; no están incrustados en los clips de cámara.
- **SFX ya producen salida:** muestra de dos segundos con voz silenciada exportada Complete; PCM decodificado con 47946 muestras no nulas, pico de muestra -15.81 dBFS (no true peak). Voz y SFX restablecidos/habilitados desde Edit y guardados. Mezcla perceptual completa pendiente. No se exportó la pieza completa.
- **Zooms/temblores pendientes en esta timeline:** la reconstrucción nativa perdió los efectos de imagen. Plan privado preparado con zoom progresivo y 13 eventos validados; dos eventos se solapaban inicialmente y el validador bloqueó la aplicación antes de modificar V1. Dynamic Zoom se activó/desactivó correctamente en una preparación; Smart Reframe alcanzó Complete en prueba, sin garantizar destino facial ni conservarlo en la entrega. No afirmar que estos efectos están aplicados en la timeline vigente.
- Resolve dejó de estar accesible durante la sesión y se reabrió con MCP. El archivo crash_archive no registra una nueva entrada posterior a 01:39:55; no se atribuye causa demostrada. Recuperación verificada sin perder los 122 títulos y 14 SFX. La revisión automática rechazó dos intentos posteriores de aplicar Fusion por relacionarlos con ese cierre. No volver a intentarlo sin resolver el bloqueo o autorización explícita nueva del usuario, informando del riesgo.
- No se llamó AddTrack. La duplicación de nodos de pista en DRT produjo pistas visibles pero sin composición/salida: descartada. Se usó importación XML nativa para registrar V1/V2 y A1/A2; después solo clips Text+ en V2 conservando registro de pistas/buses. SFX importados desde XML sin enlace se retiraron y se montaron de nuevo en A2 existente mediante MCP.
- Se limpiaron diez timelines temporales tras respaldo completo. Queda un proyecto de trabajo y una timeline. Copia final `outputs/workspace/full-editable.drp`; copia anterior a limpieza y planes/informes privados en esa carpeta. 31 pruebas aprobadas.

**Siguiente paso:** autorización informada o resolución del bloqueo antes de volver a aplicar Fusion; revisar títulos, idioma y balance sonoro directamente en Resolve. La revisión visual anterior con zooms está respaldada, pero no es la timeline vigente.

## Continuidad actual — proyecto único (2026-11-03)

El usuario aprobó la dirección visual y pidió zoom continuo hacia su rostro, un solo proyecto/timeline y revisión directa sin render habitual. Proyecto activo `AI Editor - Prueba 1`, timeline `Prueba 1 - Edicion principal`, misma muestra de 23.167 s/15 clips. Zoom con dos keyframes lineales 1.0→1.10 por clip, pivote facial aproximado (0.43,0.60), centro neutro y verificación inicial/intermedia/final. No es seguimiento facial automático ni se verificó cada frame. Se desactivaron acentos de desplazamiento brusco; se mantienen barridos blur existentes. Tres entradas distintas para 57 nodos Text+. Texto sigue dentro de Fusion de cada clip, **no en bloques independientes en una pista de texto**; esa petición de comodidad sigue pendiente. Voz y ocho SFX permanecen como clips de audio; salida mono silenciosa sigue sin resolver.

No se creó proyecto, timeline, pista ni render adicional. Respaldo antes/después y plan/informe privados en `outputs/workspace/`. Se exportaron y comprobaron archivos DRP no vacíos de 23 proyectos `AIEditor_Test_*` antes de eliminarlos de la biblioteca, según autorización del usuario; manifiesto y copias en `outputs/project-archive/`. Se conservó `New Project 1`, ajeno a estas pruebas. Sin cierres esta sesión. Treinta pruebas de regresión aprobadas y zoom verificado por API; revisar encuadre reproduciendo en Resolve.

**Próximo paso:** revisar esta única timeline con el usuario; resolver salida SFX y separar títulos en una pista editable cuando haya una vía segura sin AddTrack sobre Fusion cargado. La revisión anterior y sus renders quedan como historial.

## Revisión actual — solo prueba.MOV (2026-11-03)

El usuario rechazó el color fuerte y el movimiento insuficiente de la pieza larga, pidió una muestra corta solo con la primera fuente, transiciones/más movimiento y subtítulos cinéticos. Indicó que queda muy poco presupuesto de tokens.

- Muestra visual exportada: `outputs/kinetic/20261103_022232_cd012c4d/draft.mp4`, 23.167 s, 15 planos, 56 entradas de subtítulos (57 nodos por cruce de corte), 12 eventos (seis acentos de zoom, dos temblores, cuatro barridos con blur).
- Preset `kinetic-punch-v4`: grupos más cortos, pop/desplazamiento de entrada en todos los textos, ajuste de palabras largas para evitar recortes. Perfil `iphone-hlg-sdr-soft-v2`: timeline SDR y reducción moderada de saturación en cámara, sin cambiar el texto blanco/amarillo. Fotogramas revisados.
- Proyecto `AIEditor_Test_Kinetic_20261103_022232_cd012c4d`, timeline `Prueba 1 - kinetic style test`. No se trabajó con parte 2 ni se volvió a transcribir. Sin cierres durante esta revisión; no se llamó AddTrack.
- **Audio pendiente, no declarar resuelto:** auditoría del proyecto estéreo anterior confirmó SFX exportados a -20.31 dBFS. La nueva pista mono A2 contiene ocho clips a -6 dB, pero su exportación aislada resultó silencio (-200 dBFS). No basta subir ganancias; falta resolver salida/ruteo y comprobar la mezcla final. La muestra entregada debe considerarse visual, con voz habilitada, no mezcla sonora aprobada.
- Tras render, SetTrackEnable desde Deliver no restablecía la voz; abrir Edit y habilitar A1 sí funcionó y se comprobó antes de exportar el borrador. Hubo un AppendToTimeline con retorno nulo antes de guardar/cerrar/reabrir el proyecto; después se montaron los clips en A2 sin crear pistas.
- Exportación Complete y copia DRP guardada en la misma carpeta; el informe registra expresamente la limitación sonora.

**Próximo paso concreto:** comprobar ruteo Fairlight/bus o preparar una mezcla alternativa comprobable; no volver a tocar AddTrack ni prometer SFX audibles antes de medir una exportación aislada y escucharla. Revisar primero esta muestra visual con el usuario. Los hitos de abajo son históricos y no sustituyen estas limitaciones actuales.

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
