# AI Editor

Automatización local para producir Shorts, Reels y TikToks con DaVinci Resolve Studio, operada por un agente como Codex o Claude.

## Estado

Planificación y estructura documental inicial. Aún no hay herramientas de edición implementadas ni integración con Resolve probada en este proyecto.

Repositorio privado: [CriissGa/ai-video-editor](https://github.com/CriissGa/ai-video-editor).

## Documentación

- [Guía para agentes](AGENTS.md): reglas y contexto mínimo.
- [Arquitectura](docs/ARCHITECTURE.md): componentes, flujo y límites.
- [Estado y próximos pasos](docs/STATUS.md): punto de continuidad del trabajo.
- [Decisiones](docs/DECISIONS.md): acuerdos duraderos y motivos.
- [Página de Notion](https://app.notion.com/p/40df9c3147ed811a95c8cf8ca6eb3eb0): planificación e hitos del proyecto.

## Primer flujo propuesto

Video original → selección de un segmento por tiempos → timeline vertical editable → subtítulos con estilo → borrador exportado.

La selección automática de segmentos y una interfaz propia se evaluarán después de validar el flujo básico. El contenido inicial será grabado en vertical con cámara estática, con edición cómica rápida, subtítulos llamativos, zooms, temblores, blur y acentos sonoros.

## Uso

Abrir esta carpeta con el agente y continuar desde `docs/STATUS.md`. No existen comandos de instalación o ejecución todavía.

Los medios originales, cachés, transcripciones y exportaciones se mantendrán fuera de la documentación y del control de versiones. Su ubicación se definirá durante la primera implementación.
