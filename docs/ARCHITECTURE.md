# Arquitectura

## Dirección aceptada

Un conjunto de herramientas locales operado por un agente, con DaVinci Resolve Studio como motor de edición. El proyecto debe poder usarse desde distintos agentes sin depender del historial de un chat.

## Componentes

| Componente | Responsabilidad |
| --- | --- |
| Agente | Interpretar instrucciones, consultar material relevante y proponer decisiones editoriales |
| Plan de edición | Persistir fuentes, segmentos, tiempos, textos, estilo y destino de salida |
| Herramientas locales en Python | Validar entradas, ejecutar etapas, reutilizar resultados y registrar estado |
| Adaptador de Resolve | Traducir operaciones a la API de la instalación disponible |
| Archivos del trabajo | Conservar planes, transcripciones, resultados y versiones |
| Notion | Documentar alcance, decisiones e hitos |

## Flujo

1. Inspeccionar el material y guardar metadatos.
2. Transcribir cuando sea necesario y conservar tiempos referidos a la fuente.
3. Definir un plan de edición con intervención del usuario o del agente.
4. Validar el plan antes de ejecutar cambios.
5. Crear una timeline de trabajo en Resolve y comprobar el resultado.
6. Aplicar subtítulos y estilo dentro de las capacidades verificadas.
7. Exportar un borrador y registrar el resultado para revisión humana.

El flujo debe permitir repetir una exportación sin volver a pedir decisiones al modelo.

## Contratos propuestos

- Python para herramientas locales y JSON para planes de edición.
- Comandos locales como primera interfaz; MCP propio solo si facilita su uso después.
- MCP de Resolve existente para explorar capacidades y realizar pruebas de integración.
- Plan y resultados persistidos para continuar un trabajo desde otro agente.
- Validación de versión del plan, fuentes y rangos antes de ejecutar.
- Convención explícita de tiempos y conversión a frames según la fuente y la timeline; falta definir el esquema exacto.
- Registro de etapas completadas y artefactos producidos para reanudar sin duplicar operaciones.
- Caché vinculada al contenido de entrada y a los parámetros relevantes, con invalidación cuando cambien.

La primera herramienta implementada es `scripts/diagnose_resolve.py`: CLI de lectura para macOS, salida JSON versionada y subproceso con tiempo límite usando ResolvePython. Comprueba versión y acceso al gestor sin obtener proyectos. El resto de estas interfaces todavía no está implementado. Definir el esquema mínimo con el primer caso real, evitando generalizar antes de probarlo.

## Primer alcance propuesto

Un archivo hablado, un segmento indicado por tiempos, timeline vertical de 1080 × 1920, subtítulos sencillos y exportación de borrador. Mantener la timeline editable.

## Límites iniciales

- Sin aplicación gráfica, servidor permanente ni base de datos al inicio.
- Sin publicación automática en redes sociales.
- Selección inteligente, subtítulos animados, reencuadre automático y B-roll sujetos a validación posterior.
- No prometer paridad entre la interfaz de Resolve y su API.
- La conexión con Notion es documental mediante el agente; no hay sincronización en segundo plano.

## Verificación pendiente

Versión y acceso de scripting confirmados con Studio 21.1.2.10 (ver `RESOLVE_DIAGNOSTIC.md`). Pendiente: importación, montaje por rangos, subtítulos y render. Después probar tres videos representativos y medir correcciones manuales, tiempo de proceso y consumo de IA.

## Dirección creativa y eventos de edición

Entrada confirmada: videos verticales con cámara estática y el usuario a cámara. Montaje cómico rápido inspirado en recursos de Rubius y HolaSoyGerman, con identidad propia moderna. Recursos: subtítulos con color selectivo, frases destacadas, zooms, temblores, blur, transiciones y efectos sonoros.

El plan deberá describir eventos con tiempo, duración, intensidad y referencias a presets y sonidos reutilizables. Validar cada recurso en Resolve. Preservar rostro, legibilidad, voz y pausas cómicas. Evaluar seguimiento facial según el movimiento real: cámara estática no significa rostro inmóvil.
