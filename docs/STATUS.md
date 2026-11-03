# Estado del proyecto

## Situación actual

Fase: primer diagnóstico local completado. CLI reutilizable en `scripts/diagnose_resolve.py`, sin dependencias externas. Conexión real de lectura verificada; no hay código de edición todavía.

Repositorio privado creado: https://github.com/CriissGa/ai-video-editor. Git y GitHub CLI (`gh`) están disponibles y la autenticación fue verificada. La documentación inicial y `.gitignore` constituyen el primer hito versionado.

El usuario autorizó commits y push al cerrar hitos verificados y pidió usar terminal con `git`/`gh`, evitando Computer Use para estas tareas. La regla quedó registrada en `AGENTS.md` y se añadió `.gitignore`.

## Confirmado

- El usuario quiere producir Shorts, Reels y TikToks con eficiencia y consumo controlado de tokens.
- El usuario dispone de una licencia de DaVinci Resolve Studio.
- Se aceptó la dirección de herramientas locales operadas por Codex o Claude.
- Se creó una página de Notion para documentar el proyecto; enlace en `README.md`.
- Se crearon instrucciones compartidas y documentos de arquitectura, estado y decisiones.

## Pendientes que afectan el alcance

- Video de muestra y referencia del resultado deseado.
- Importación, montaje, subtítulos y render todavía sin comprobar.
- Afinar tipografía, paleta e intensidad de efectos con una muestra.
- Ubicación de medios y artefactos de trabajo.
- Presupuesto y límites de IA, después de medir un caso representativo.

## Siguiente paso

Elegir un clip vertical y un segmento por tiempos; definir el plan JSON mínimo y su validación antes de probar importación, montaje y render en un proyecto de prueba separado.

## Orden de implementación propuesto

1. Conexión básica verificada; validar capacidades de edición en proyecto de prueba.
2. Definir el plan JSON mínimo y su validación.
3. Ejecutar cortes indicados manualmente y exportar un borrador editable.
4. Añadir subtítulos y estilo reutilizable.
5. Medir el flujo con tres videos.
6. Añadir selección con IA y, si aporta valor, una interfaz MCP propia.

## Última actualización

Hito de diagnóstico (2026-11-03, America/Phoenix): instalación 21.1.2; API real DaVinci Resolve Studio 21.1.2.10, gestor accesible, ResolvePython 3.14.4, salida `ok` y código 0 fuera del sandbox. Dentro del sandbox devolvió `unreachable` aun con Resolve abierto. Se inició la aplicación y se dejó abierta; no se ejecutaron llamadas de apertura, creación, guardado o modificación de proyectos. Tres pruebas unitarias aprobadas. Detalles y límites en `docs/RESOLVE_DIAGNOSTIC.md`. No se usaron medios reales.

## Dirección creativa confirmada

Humor con cortes rápidos y referencias Rubius + HolaSoyGerman adaptadas a una identidad propia. Subtítulos con color puntual, frases destacadas, zooms, temblores, blur, transiciones y acentos sonoros. Priorizar rostro visible, voz clara y timing cómico. Próximo paso: un clip de muestra para calibrar el estilo y validar los efectos en Resolve.
