# Guía para agentes

## Proyecto

AI Editor automatiza la producción de Shorts, Reels y TikToks usando DaVinci Resolve Studio, herramientas locales y un agente como Codex o Claude. Priorizar resultados editables, funcionalidad y consumo medido de tokens. No se requiere una aplicación ni un servidor permanente para comenzar.

## Contexto mínimo

- Leer `docs/STATUS.md` al comenzar para conocer el estado y el siguiente paso.
- Consultar `docs/ARCHITECTURE.md` cuando la tarea afecte componentes o interfaces.
- Consultar `docs/DECISIONS.md` antes de cambiar una decisión arquitectónica.
- `README.md` es la entrada para personas. No cargar toda la documentación en cada tarea.
- La conversación actual del usuario tiene prioridad sobre estos archivos. Distinguir propuestas, decisiones aceptadas y resultados verificados.

## Forma de trabajar

- Construir herramientas reutilizables con parámetros; evitar generar scripts distintos por video.
- Usar un plan de edición persistido como entrada del ejecutor. El agente propone; las herramientas validan y ejecutan.
- Comenzar por un flujo completo pequeño antes de ampliar el alcance o crear una interfaz.
- Verificar la API disponible en la instalación antes de asumir que una función de Resolve es automatizable.
- Validar archivos, tiempos, pistas y parámetros antes de modificar una timeline.
- Usar proyectos o timelines de prueba para experimentos. No sobrescribir originales, timelines del usuario ni exportaciones existentes por defecto.
- Registrar resultados y errores concisos. No afirmar que una operación se completó sin comprobarla.
- Ejecutar comprobaciones proporcionadas al cambio. No añadir infraestructura o dependencias sin una necesidad concreta.

## Tokens y procesamiento

- Reutilizar transcripciones y análisis si el archivo y la configuración siguen vigentes.
- Dar al modelo texto con tiempos y fragmentos relevantes; usar análisis visual cuando la tarea lo requiera.
- Ejecutar importación, montaje, render y espera de trabajos con código local, sin ciclos de razonamiento por operación.
- Limitar llamadas y reintentos. Ante errores repetidos, diagnosticar antes de repetir.
- Separar métricas de consumo de IA, tiempo de ejecución y esfuerzo manual. No inventar costos ni ahorros.
- No incluir medios completos, transcripciones extensas, secretos ni logs masivos en documentación o contexto por defecto.

## Git y publicación de avances

- El usuario autoriza hacer commit y push automáticamente al cerrar cada hito coherente y verificado de este proyecto, sin pedir confirmación de nuevo. Esto es una instrucción para el agente activo, no un proceso en segundo plano.
- Antes de publicar: revisar `git status`, los cambios y el diff preparado; ejecutar las comprobaciones pertinentes y actualizar el estado/documentación afectados.
- Incluir solo archivos relacionados con la tarea. No incorporar cambios ajenos, secretos, medios originales, transcripciones privadas, cachés ni exportaciones.
- Usar commits pequeños con mensajes descriptivos. Hacer push a la rama de trabajo y al remoto de este proyecto; respetar protecciones y usar PR cuando corresponda.
- No usar force push, reescribir historial, borrar ramas remotas ni resolver conflictos descartando cambios del usuario. Si hay divergencia o falla autenticación, conservar los commits e informar el bloqueo.
- Verificar que el commit local coincide con la rama remota antes de informar que el push terminó. Si no hay cambios, no crear commits vacíos.
- Las instrucciones actuales del usuario y las restricciones del entorno siguen teniendo prioridad.
- Para Git y GitHub, usar la terminal con `git` y `gh`. El usuario prefiere evitar Computer Use para estas actividades por consumo de tokens.

## Documentación y continuidad (mantenimiento)

- Al cerrar un hito o cambiar un bloqueo, actualizar `docs/STATUS.md` con hechos y un próximo paso concreto.
- Registrar decisiones duraderas aceptadas en `docs/DECISIONS.md`; no copiar conversaciones completas.
- Actualizar arquitectura cuando cambien las responsabilidades o contratos.
- Notion contiene documentación de hitos; los archivos locales contienen el estado técnico del proyecto. Enlace en `README.md`.
- Actualizar Notion al cerrar hitos relevantes cuando la conexión esté disponible. Si falla, conservar el avance local e informar; no bloquear el trabajo técnico.
- Nunca afirmar que existe sincronización automática con Notion: todavía no está implementada.
- Si dos fuentes discrepan, indicar la discrepancia y resolverla con la instrucción más reciente del usuario y evidencia verificable.

## Estilo confirmado

Videos grabados en vertical con cámara estática y el usuario a cámara. Humor rápido inspirado en recursos de Rubius y HolaSoyGerman, con identidad propia moderna. Subtítulos llamativos con color selectivo, frases destacadas, zooms, temblores, blur, transiciones y efectos sonoros. Mantener rostro visible, voz clara y pausas cómicas; elegir efectos según el remate, sin cadencias fijas. Retención como objetivo a medir, sin garantías.


El usuario habla español e inglés y puede mezclarlos o equivocarse al hablar como parte del humor. Preservar idioma, acento, cambios de idioma y errores hablados; no traducir ni corregir gramática automáticamente. Distinguir errores del reconocimiento de voz (corregibles tras verificar audio) de lo que realmente dijo. Preferencia confirmada: subtítulos más grandes, borde negro y algo de sombra; zooms y temblores perceptibles elegidos por remate.


Dirección adicional confirmada: edición más alegre y exagerada, palabras importantes de mayor tamaño y contornos más gruesos. Los sonidos aportados en `sonidos/` son medios locales privados; seleccionar y recortar según cortes/remates, en pista SFX independiente, sin tapar la voz. Ante cierres de Resolve, conservar avances, diagnosticar y preferir operaciones MCP separadas. La ejecución nativa con SFX quedó bloqueada explícitamente tras dos fallos Qt observados; no repetirla sin resolver la causa.


Para la historia actual, el usuario pidió unos 2–2½ minutos; no es una duración fija para todos los videos. Preferencias de estilo: zooms progresivos con keyframes además de acentos rápidos, y SFX más audibles. Videos iPhone de ambas partes verificados como Rec.2100 HLG: normalizar técnicamente a SDR/Rec.709 antes de afinar el look creativo. El MCP también sufrió un cierre en AddTrack tras Fusion; ya no crear pistas en timelines cargadas. Reutilizar una pista vacía compatible (SFX mono cuando sea necesario) y verificar que no cambió el número de pistas. No declarar resuelta la causa del crash por cambiar de protocolo.


Preferencia actual: trabajar en un solo proyecto/timeline (`AI Editor - Prueba 1`), revisar directamente en Resolve sin renderizar cada cambio y mantener todo editable. Zooms progresivos suaves desde encuadre completo hacia la cara; no perder encuadre. Variar animaciones de texto. El usuario quiere subtítulos como elementos accesibles de timeline; Fusion por clip es la implementación actual, no dar por satisfecha una pista independiente. Limpieza de proyectos de prueba propios autorizada, con respaldo DRP previo.
