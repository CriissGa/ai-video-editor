# Palabras destacadas y sonidos locales

## Dirección y preset

El usuario pidió un estilo más alegre y exagerado: palabras importantes más grandes, borde más grueso y sonidos aportados en `sonidos/`. Preservar voz, errores hablados y mezcla español/inglés. Se mantiene la misma selección para comparar estilo.

`bold-party-v3` conserva los presets anteriores. Texto normal 0.105, importante 0.14 (33 % mayor que el normal), borde negro 0.075 (50 % más grueso que v2) y sombra suave. Las palabras importantes tienen un pequeño pop de tamaño durante seis frames, con sobreimpulso del 12 %. Máximo dos líneas de 16 caracteres. El generador separa palabras de foco de la frase, manteniendo las palabras y sus tiempos; no corrige gramática. La lista inicial bilingüe es parametrización editorial del preset y puede ampliarse; no constituye selección semántica automática universal.

```sh
python3 scripts/prepare_captions.py PLAN_V1 TRANSCRIPCION outputs/plan-alegre.json --preset bold-party-v3
python3 scripts/prepare_sounds.py sonidos --output-dir outputs/sounds
```

El segundo comando usa `afconvert` de macOS, sin dependencias nuevas. En este entorno CoreAudio falla dentro del sandbox (`fmt?`), pero fuera convierte correctamente. Produce copias PCM16 estéreo/48 kHz identificadas por SHA-256 y `catalog.json` con duración, pico de muestras y regiones activas sugeridas. Conserva los originales. El catálogo mide actividad, no escucha ni clasifica el contenido de forma perceptual. Se usaron nombres y regiones para la primera selección; escuchar la mezcla sigue siendo necesario.

## Contrato de audio en plan v2

Campo raíz opcional `audio` con:

- `dialogue_gain_db`: -12 a 0 dB.
- `sounds`: 1–40 entradas con `source`, `in_seconds`, `out_seconds`, `at_seconds`, `gain_db`, `fade_in_frames`, `fade_out_frames`.

`source` es WAV PCM16 estéreo/48 kHz; rutas relativas al plan o absolutas. Entrada/salida se refieren al sonido fuente; `at_seconds` se refiere al montaje final. Conversión a frames half-up, intervalo [entrada, salida). Los recortes deben caber en el archivo y en la timeline, no pueden superponerse en la pista SFX. Ganancia -36 a -6 dB, fundidos enteros de 0 a un segundo, cuya suma no exceda la duración del clip. Se valida antes de modificar timeline.

`sound_edit.import_sounds` importa y comprueba FPS. `sound_edit.apply_audio` crea una pista estéreo independiente llamada `AI Editor - SFX`, ajusta voz en A1 y monta recortes con `recordFrame` absoluto. Comprueba duración, offset, posición, ganancia, fundidos y cantidad. `verify_timeline` conserva las comprobaciones del montaje de voz/video y admite solo la pista SFX validada como excepción entre pistas adicionales.

## Ruta verificada y cierre de Resolve

**La CLI permite validar planes con audio, pero bloquea su ejecución nativa antes de conectar a Resolve.** Dos intentos con el worker local cerraron Studio 21.1.2.10 con `ASSERT failure in QList::insert` en Qt. La primera ejecución guardó los textos; la segunda falló durante importación y dejó un worker esperando. No se ha probado una causa única ni una solución general. Una prueba mínima de AddTrack sí funcionó; no atribuir el cierre únicamente a crear pistas.

Se detuvo solo el worker bloqueado. Tras el segundo cierre la aplicación quedó en modo de reporte; el usuario cerró el aviso y la volvió a abrir. Se recuperó el proyecto de prueba guardado y se completaron sonidos/exportación con el MCP en llamadas separadas. Esa es la ruta efectivamente verificada para SFX. El worker de CLI sin audio tiene ahora timeout externo de render-timeout + 120 s para no esperar indefinidamente tras perder conexión. No repetir automáticamente los lotes que provocaron el fallo.

Operación desde MCP: cargar el plan con `edit_video.load_plan`, comprobar proyecto de prueba, fuente y montaje; reutilizar los MediaPoolItems ya importados, llamar `sound_edit.apply_audio`, verificar con `verify_timeline(..., allowed_audio_tracks=[track])`, guardar y exportar usando `edit_video.export_draft`. Leer/escribir plan e informe requiere `run_script_unsafe`; las llamadas API sin archivos usan `run_script`. Revisar primero si la pista SFX ya contiene clips: no volver a aplicar y duplicarlos. El proyecto final de este hito ya tiene los cinco efectos.

No se afirma que el flujo nativo completo con audio sea estable. El código separa validación, montaje y exportación para operar las etapas mediante el MCP y conservar informes. Los fotogramas del preset v3 se exportan después de la edición, en llamadas de revisión separadas, en vez de intercalarlos con cambios de nodos.

## Resultado comprobado

2026-11-03, America/Phoenix. Proyecto final `AIEditor_Test_Playful_20261103_010423_81a230c0`, timeline `Hair story - playful words and SFX`, guardado y dejado abierto en Edit. Artefactos privados en `outputs/playful/mcp_20261103_011224_b0cb313c/`: plan, informe, SRT, MP4, DRP y fotogramas. El informe identifica la recuperación mediante MCP, no una ejecución nativa exitosa.

- 695 frames / 23.167 s, 35 textos Text+ y palabras de foco con mayor tamaño/pop; contorno 0.075 en todos los textos.
- Tres zooms y dos temblores, algo más intensos, sobre el video; textos estables salvo pop de entrada de palabras destacadas.
- Cinco clips SFX usando cuatro archivos de los siete aportados: tres acentos de transición y dos clicks de remate. Pista A6, recortes de 9–12 frames, ganancias -20/-18 dB, fundidos de 1/2 frames. Voz a -3 dB.
- Render Complete al 100 %, 10292 ms; exportación medida 11.842 s, sin incluir fallos/desarrollo. MP4 24 094 690 bytes, H.264, vertical 1080 × 1920 a 30 fps, AAC estéreo, reimportado y comprobado.
- Audio exportado decodificado a PCM: duración 23.188 s (relleno de AAC), pico de muestra -2.93 dBFS. Es una medida de pico de muestras, no true peak ni validación perceptual de mezcla.
- DRP reimportado en otro proyecto de prueba: 35 textos, borde grueso y cinco sonidos online conservados. Fotogramas revisados de tres palabras importantes; no se inspeccionó cada frame ni se escuchó el video completo.

Pendiente: revisión humana de tamaño/ritmo, selección sonora y balance voz/SFX. Preservar `prueba.MOV` y las copias WAV usadas por el DRP; `sonidos/`, `outputs/`, transcripciones y planes reales no se publican en Git.
