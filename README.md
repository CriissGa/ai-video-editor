# AI Editor

Automatización local para producir Shorts, Reels y TikToks con DaVinci Resolve Studio, operada por un agente como Codex o Claude.

## Estado

Primer flujo de edición implementado y verificado con DaVinci Resolve Studio 21.1.2.10: plan JSON validado, importación, cortes, transcripción cacheada, subtítulos Fusion editables, texto grande con borde/sombra, zooms animados, temblores y borrador MP4.

Repositorio privado: [CriissGa/ai-video-editor](https://github.com/CriissGa/ai-video-editor).

## Documentación

- [Guía para agentes](AGENTS.md): reglas y contexto mínimo.
- [Arquitectura](docs/ARCHITECTURE.md): componentes, flujo y límites.
- [Estado y próximos pasos](docs/STATUS.md): punto de continuidad del trabajo.
- [Decisiones](docs/DECISIONS.md): acuerdos duraderos y motivos.
- [Página de Notion](https://app.notion.com/p/40df9c3147ed811a95c8cf8ca6eb3eb0): planificación e hitos del proyecto.

## Primer flujo disponible

Video original → plan JSON con segmentos por tiempos → proyecto de prueba y timeline vertical editable → borrador MP4 y copia DRP. La primera muestra con subtítulos y zooms está disponible; falta calibrar el estilo con revisión humana.

La selección automática de segmentos y una interfaz propia se evaluarán después de validar el flujo básico. El contenido inicial será grabado en vertical con cámara estática, con edición cómica rápida, subtítulos llamativos, zooms, temblores, blur y acentos sonoros.

## Uso

Abrir esta carpeta con el agente y continuar desde `docs/STATUS.md`. Para comprobar la conexión en macOS con Resolve abierto:

```sh
python3 scripts/diagnose_resolve.py
```

Sin paquetes adicionales. Consulta [uso, resultados y resolución de errores](docs/RESOLVE_DIAGNOSTIC.md).

Para validar y ejecutar el plan de muestra con el video local:

```sh
python3 scripts/edit_video.py plans/first-draft.json
python3 scripts/edit_video.py plans/first-draft.json --execute
```

Consulta [contrato JSON, resultados y límites](docs/EDIT_WORKFLOW.md). Cada ejecución crea un proyecto de prueba nuevo y una carpeta exclusiva bajo `outputs/first-draft/`. Los medios, DRP e informes generados quedan fuera de Git.


Para transcribir localmente y reutilizar los tiempos:

```sh
python3 scripts/transcribe_video.py prueba.MOV
```

Consulta [subtítulos, plan v2 y preset de estilo](docs/CAPTIONS_WORKFLOW.md). Los textos reales, planes editoriales y transcripciones se guardan en carpetas privadas excluidas de Git; el ejemplo versionado usa textos ficticios.
