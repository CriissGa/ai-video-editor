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

Estado: propuesta técnica inicial; pendiente de validar con el primer flujo.

Empezar con Python, planes JSON y comandos locales. Añadir un MCP propio después si mejora la operación desde los agentes.

Motivo: implementar y depurar el flujo mínimo con pocas piezas y permitir reutilizar las mismas herramientas desde distintas interfaces.

## D005 — Versionado y publicación por hitos

Estado: aceptada por el usuario.

Usar Git y GitHub CLI desde terminal. Hacer commit y push automáticamente al completar hitos coherentes y verificados, incluyendo solo cambios de la tarea. No usar force push ni publicar secretos, medios originales o artefactos generados. Repositorio privado: CriissGa/ai-video-editor.
