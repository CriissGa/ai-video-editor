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
