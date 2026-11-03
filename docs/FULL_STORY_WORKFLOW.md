# Historia multi-fuente, movimiento progresivo y color

## Alcance solicitado

El usuario pidió integrar la segunda parte, subir los SFX, añadir el zoom gradual que hacía con keyframes y revisar la diferencia de color al exportar material del iPhone. Aclaró que desea una versión completa de unos 2–2½ minutos. Se seleccionó una historia de 2:01.967 con presentación, preparación, aplicación y el estado final que aparece en el material disponible. No se inventó una toma posterior de resultado lavado/seco.

La segunda fuente dura 24:24:09 a 30 fps, 43929 frames; la primera 3635 frames. Ambas son 1080 × 1920, 30 fps, seis canales de audio y se identifican en Resolve como Rec.2100 HLG/H.265 10-bit. No se infiere solo por provenir de un iPhone. La segunda transcripción local contiene 775 palabras y está persistida con hash/configuración; se reutilizó la primera. Los pasajes mixtos y errores de ASR requieren revisión contra audio; se mantienen los errores hablados como recurso creativo.

## Plan JSON v3

`edit_video.load_plan` admite v1/v2 y delega v3 a `story_plan.validate_story`. El v3 tiene:

- `sources`: diccionario de 1–10 identificadores a rutas de video.
- `segments`: campos `source`, `in_seconds`, `out_seconds`, `zoom`, `zoom_end`.
- `timeline`, `project_prefix`, `output_dir`, `captions` y `style` como en v2.
- `color: {"preset": "iphone-hlg-to-sdr-v1"}`.
- `audio` opcional, con el contrato anterior y soporte PCM mono/estéreo.

Valida archivos, identificadores, referencias, tiempos, FPS de timeline y zoom inicial/final 1–1.2, además de subtítulos, efectos y audio. Al importar cada medio se contrastan resolución, FPS, audio y rangos reales antes de crear la timeline. `verify_story` comprueba cantidad, posiciones, duración y offset en video/voz y también la identidad del archivo fuente de cada clip.

`story_plan.create_story_project` crea un proyecto nuevo, configura color, importa fuentes y monta segmentos en orden. Se opera mediante MCP por etapas, guardando después de cada lote. La CLI v3 valida, pero la ejecución se remite explícitamente al MCP. No hay selección editorial automática ni reanudación que descarte o rehaga silenciosamente composiciones ya existentes.

## Zoom gradual editable

`caption_style.apply_style` acepta rangos de clips para aplicar estilo por lotes sin duplicar nodos. Para un segmento con `zoom_end` distinto de `zoom`, añade un modificador BezierSpline al Transform de imagen y asigna keyframes al primer/último frame. Comprueba inicio, mitad y final. Los acentos rápidos van en otro Transform, para no sustituir los keyframes progresivos. Los textos se componen después y mantienen su legibilidad.

En esta historia: 21 clips, 14 zooms progresivos, 121 textos Text+ con el preset de palabras de foco; también se conservan acentos rápidos y temblores elegidos por remate. No todos los clips reciben el mismo movimiento.

## Base técnica de color

`color_pipeline.py` contiene el preset verificado en esta instalación:

- DaVinci YRGB Color Managed v2, modo Custom, entrada HLG explícita por medio.
- Timeline DaVinci Wide Gamut/Intermediate.
- Salida Rec.709 Gamma 2.4; output DRT DaVinci y límite de salida 100 nits.
- Exportación etiquetada Rec.709 / Gamma 2.4.

Se contrasta el valor leído tras cada ajuste. El campo de gamut mapping descrito en el stub rechazó el valor probado y no se usa; no se afirma que se configuró una opción no aceptada.

El render inicial mostró que la transformación apagaba los gráficos Fusion. Se comprobó una compensación de luminancia 4.0 **solo en la paleta de los nodos Text+** de este perfil; no cambia MediaIn, piel ni exposición del video. Está persistida en código y en el informe, y se aplica al generar nuevos textos o a los existentes tras comprobar su identidad. Se compararon blanco y amarillo en fotogramas. Es una adaptación de gráficos probada en esta configuración, no una constante universal para otros proyectos/versiones.

Esto establece una base HLG→SDR coherente antes del acabado creativo. No garantiza idéntica apariencia entre la reproducción HDR del iPhone y todos los reproductores/pantallas SDR. No se hizo calibración de monitor ni se promete un etalonaje final; el look y el balance entre tomas se afinarán tras revisar la pieza completa. No se añadió una LUT destructiva a los originales.

## Cierre observado y alternativa comprobada

El MCP también cerró Resolve al ejecutar `AddTrack` después de montar Fusion en la historia larga (registro de cierre 2026-11-03 01:39:55 del equipo). La llamada devolvió fallo y quedó guardado el montaje con sus 21 clips/textos. Por tanto, el cambio a MCP por sí solo **no resuelve** el problema Qt observado previamente. El usuario cerró el aviso y reabrió la aplicación.

Se eliminó la llamada AddTrack del adaptador de sonidos. `choose_sfx_track` exige una pista existente, vacía y con formato compatible. Si no existe, falla de forma explícita antes de montar sonidos. No crea una pista sobre una timeline con Fusion. `prepare_sounds.py --channels 1` produce copias mono separadas, sin sobrescribir las copias estéreo ni originales. La primera pista vacía disponible era A2 mono: se importaron dos copias mono y se colocaron nueve sonidos; la cantidad de pistas se mantuvo en cinco. Esta alternativa se completó sin repetir el cierre. La causa interna de Qt no se considera resuelta ni se habilita la ruta nativa con audio.

SFX a -14/-12 dB frente a -20/-18 dB en la muestra anterior (+6 dB), fundidos 1/2 frames y voz a -3 dB. Se conserva salida estéreo, aunque los efectos de esta versión sean mono. `pcm_peak` mide el pico de muestras en streaming sin límite de 60 s; no mide true peak ni comprensión perceptual.

## Exportación y revisión

`export_draft(..., wait=False)` prepara y guarda el trabajo antes de iniciar render, devuelve su ID y permite revisar su estado después. Guardar durante render fue rechazado por esta instalación; se corrigió el orden y se añadió prueba de regresión. No se debe volver a encolar el mismo trabajo al recibir ese error: primero consultar el ID guardado.

Artefactos finales y evidencia de revisión se detallan en `STATUS.md`. El DRP requiere conservar ambas fuentes y las copias PCM usadas. Medios, transcripciones y planes reales permanecen fuera de Git.
