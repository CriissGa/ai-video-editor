# Registro de decisiones

Registrar aquí acuerdos duraderos. Cada entrada distingue decisiones aceptadas de propuestas pendientes; actualizar o sustituir una decisión explícitamente si cambia.

## D001 — Herramientas locales operadas por un agente

Estado: aceptada como dirección del proyecto.

Usar DaVinci Resolve Studio como motor, con una capa de herramientas reutilizables que un agente pueda operar. No construir una aplicación propia para el inicio.

Motivo: aprovechar la licencia y las capacidades de edición existentes, conservando un resultado editable y reduciendo el trabajo inicial.

## D002 — Separar decisiones editoriales de ejecución

Estado: aceptada como dirección del proyecto.

Persistir un plan de edición y ejecutar operaciones repetitivas con herramientas locales. Reservar la intervención del modelo para interpretación y criterio editorial.

Motivo: facilitar revisión, repetición y continuidad entre agentes, evitando llamadas de IA por cada operación.

## D003 — Notion para documentación del proyecto

Estado: aceptada; página inicial creada.

Mantener planificación e hitos en Notion y el estado técnico junto al proyecto. Los cambios se realizan mediante el agente; no se ha configurado sincronización automática.

Motivo: contar con documentación consultable sin hacer depender la ejecución técnica de un servicio externo.

## D004 — Python, JSON y comandos locales

Estado: aceptada y validada con el primer flujo solicitado por el usuario (2026-11-03).

Empezar con Python, planes JSON y comandos locales. Añadir un MCP propio después si mejora la operación desde los agentes.

Motivo: implementar y depurar el flujo mínimo con pocas piezas y permitir reutilizar las mismas herramientas desde distintas interfaces.

## D005 — Versionado y publicación por hitos

Estado: aceptada por el usuario.

Usar Git y GitHub CLI desde terminal. Hacer commit y push automáticamente al completar hitos coherentes y verificados, incluyendo solo cambios de la tarea. No usar force push ni publicar secretos, medios originales o artefactos generados. Repositorio privado: CriissGa/ai-video-editor.


## D006 — Contrato mínimo de montaje v1

Estado: implementado y verificado para el primer flujo solicitado.

Una fuente vertical con audio, tiempos en segundos relativos al inicio, intervalos [entrada, salida), redondeo half-up a frames y FPS enteros iguales entre fuente y timeline. Montaje secuencial en el orden del plan; sin conversión de FPS en esta versión. Contrato completo en `EDIT_WORKFLOW.md`.

Cada ejecución crea un proyecto `AIEditor_Test_…` y salida exclusiva; conserva plan, informe, DRP y MP4. Repetir crea otra ejecución, no reanuda ni sobrescribe. Esta primera implementación registra etapas para diagnóstico; la reanudación automática sigue pendiente. Sin subtítulos o efectos en este hito.


## D007 — Primera implementación de subtítulos y caché

Estado: implementada y verificada en la continuación autorizada por el usuario; preset propuesto para revisión.

Usar transcripción nativa local de Resolve con caché por hash del archivo, versión e idioma/configuración. Persistir texto y planes con palabras del usuario solo en carpetas privadas excluidas de Git. Mantener el idioma original en la primera muestra.

Plan v2 compatible con el ejecutor v1: zoom por segmento, preset nombrado y subtítulos con tiempos relativos a la timeline. Implementar los subtítulos como Text+ editables dentro de Fusion, con SRT adicional sin formato. No son una pista nativa de subtítulos. Texto blanco, énfasis amarillo por frase y contorno negro son una propuesta de estilo ajustable; el usuario aún no ha aprobado esta muestra.


## D008 — Voz bilingüe y revisión visual

Estado: preferencia creativa confirmada por el usuario (2026-11-03); nueva muestra pendiente de revisión.

Preservar el español/inglés mezclado, el acento y equivocaciones al hablar como recursos de humor. Corregir errores de transcripción solo al contrastarlos con el audio, sin normalizar automáticamente la gramática ni traducir. La transcripción automática por idioma dominante no se considera resuelta para todos los pasajes mixtos.

Aumentar subtítulos, mantener borde negro y añadir sombra suave. Usar zooms animados y temblores breves según remates, sin cadencia fija. Preset `bold-yellow-v2` separado del anterior para conservar reproducibilidad: tamaño 0.10, contorno 0.05, sombra negra semitransparente. Eventos explícitos en tiempo de timeline, implementados sobre el video antes de los textos para mantener legibilidad.


## D009 — Palabras de foco y biblioteca sonora local

Estado: dirección creativa solicitada; muestra verificada y pendiente de revisión del usuario.

Usar un preset nuevo más alegre/exagerado, con palabras importantes mayores, pop de entrada, borde más grueso y sonidos elegidos según cortes/remates. Conservar presets anteriores. Biblioteca `sonidos/` privada, con copias de trabajo y selección persistida en el plan, pista SFX independiente y ganancias/fundidos ajustables; no añadir sonidos con cadencia fija.

Restricción verificada de implementación: tras dos cierres Qt al ejecutar el flujo nativo con audio, bloquear esa ruta de CLI y completar etapas mediante MCP. La recuperación/exportación por MCP está comprobada; la causa del fallo nativo sigue sin aislarse y no se declara resuelta.


## D010 — Historia multi-fuente y base de color antes del look

Estado: implementada para la versión completa solicitada; duración específica de esta pieza 2–2½ minutos.

Plan v3 con identificadores de fuente, rangos y zoom inicial/final por segmento; validar antes de crear timeline y comprobar identidad real de cada clip. Mantener v1/v2. Zoom progresivo mediante keyframes, con acentos en un Transform separado. Montaje por lotes y exportación no bloqueante mediante MCP.

Verificar el perfil real del archivo: ambas fuentes iPhone se identificaron HLG. Normalizar HLG→SDR/Rec.709 Gamma 2.4 antes del acabado creativo, conservando gestión de color editable y etiquetas correctas. La adaptación de luminancia de títulos es específica del perfil probado; no se aplica a cámara ni se promete igualdad entre pantallas HDR y reproductores SDR.

El nuevo cierre AddTrack por MCP sustituye la idea de que bastaba cambiar protocolo: el adaptador no crea pistas en timelines cargadas. Reutilizar una vacía compatible y, si hace falta, preparar copias mono de SFX. La causa interna sigue abierta y la ejecución nativa con audio permanece bloqueada.


## D011 — Calibración corta y validación sonora real

El usuario pide trabajar solo con `prueba.MOV` para ahorrar tokens, color más suave y edición mucho más dinámica. Conservar presets anteriores y probar variantes cortas antes de volver a una pieza larga. No prometer ausencia de aburrimiento o paridad estilística solo por contar efectos. La presencia de SFX en timeline no prueba que sean audibles: verificar un stem exportado; el mono resultó silencioso y queda pendiente de ruteo.


## D012 — Un proyecto de trabajo y revisión sin render

Preferencia explícita del usuario: continuar en un solo proyecto con una timeline, audio visible/editable y zoom continuo conservador hacia la cara. No generar otro proyecto o render en cada iteración. Conservar copias DRP antes de limpiar proyectos de prueba propios. Variar entradas de texto. Los títulos Fusion actuales no equivalen a bloques independientes en pista; queda pendiente esa mejora. No añadir pistas en la timeline Fusion cargada.


## D013 — Text+ independientes y separación de efectos

Solicitud explícita: títulos Text+ individuales en V2, imagen/zooms en V1 y SFX en una sola pista A2. Mantener español/inglés originales; el usuario confirmó el saludo español. Montaje completo de la primera fuente con esperas recortadas. Revisar en Resolve sin render rutinario; se admite una muestra diagnóstica breve para comprobar audio. No declarar completados zooms/temblores mientras la aplicación Fusion esté bloqueada por revisión automática.


## D014 — Movimiento marcado y recorte de silencios protegido

El usuario reiteró los efectos tras la pregunta sobre el riesgo; prueba de un clip y luego lotes pequeños con respaldo. Usar zoom progresivo más acentos breves/temblores y barridos de blur en cambios de sección, con rostro visible y títulos independientes estables. Silencios refinados con energía local y protección de palabras, conservando revisión humana. Destacados mayores y tres entradas más marcadas; ajustar palabras largas para que quepan. No usar AddTrack ni generar proyectos nuevos. Una ejecución sin cierre no resuelve la causa de los fallos históricos.


La revisión posterior solicitó más frecuencia de acercamientos/barridos y doce sonidos adicionales en la misma timeline. Esos valores se guardan en el plan de esta edición; no fijan una cadencia universal del estilo. Preferir actualizar nodos existentes frente a reconstruir el montaje al cambiar intensidad.
