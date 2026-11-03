#!/usr/bin/env python3
"""Valida un plan y ejecuta un montaje en un proyecto nuevo de Resolve."""
import argparse
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import time

# ResolvePython no añade automáticamente la carpeta del script a sys.path.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from diagnose_resolve import diagnose

APP = Path('/Applications/DaVinci Resolve/DaVinci Resolve.app')


def require(ok, message):
    if not ok:
        raise ValueError(message)


def keys(value, expected):
    require(isinstance(value, dict) and set(value) == set(expected),
            'Campos inválidos; esperados: ' + ', '.join(expected))


def number(value):
    return type(value) in (int, float) and math.isfinite(value)


def load_plan(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, 'Campo JSON duplicado: ' + key)
            result[key] = value
        return result
    plan = json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique)
    return validate_plan(plan, path)


def validate_plan(plan, path):
    require(isinstance(plan, dict), 'Plan debe ser un objeto')
    version = plan.get('schema_version')
    require(type(version) is int and version in (1, 2, 3), 'Versión no soportada')
    if version == 3:
        from story_plan import validate_story
        return validate_story(plan, path)
    fields = ['schema_version', 'source', 'project_prefix', 'timeline', 'segments', 'output_dir']
    keys(plan, fields + (['captions', 'style'] + (['audio'] if 'audio' in plan else []) if version == 2 else []))
    require(isinstance(plan['project_prefix'], str) and
            re.fullmatch(r'AIEditor_Test_[A-Za-z0-9_-]{1,50}', plan['project_prefix']), 'Prefijo de proyecto de prueba inválido')
    for key in ('source', 'output_dir'):
        require(isinstance(plan[key], str) and bool(plan[key]), 'Ruta inválida: ' + key)
        plan[key] = str((path.parent / plan[key]).resolve())
    source = Path(plan['source'])
    require(source.is_file() and source.stat().st_size > 0, 'Fuente ausente o vacía')
    require(source.suffix.lower() in ('.mov', '.mp4', '.mkv'), 'Formato de entrada no soportado')
    output = Path(plan['output_dir'])
    require(not output.exists() or output.is_dir(), 'Destino no es una carpeta')
    require(source.parent != output, 'Usar carpeta de salida separada de los originales')
    keys(plan['timeline'], ['name', 'width', 'height', 'fps'])
    tl = plan['timeline']
    require(isinstance(tl['name'], str) and 0 < len(tl['name']) <= 100, 'Nombre de timeline inválido')
    require(type(tl['width']) is int and type(tl['height']) is int and
            0 < tl['width'] < tl['height'] <= 3840 and tl['width'] % 2 == tl['height'] % 2 == 0,
            'Resolución vertical par requerida, máximo 3840')
    require(number(tl['fps']) and tl['fps'] in (24, 25, 30, 50, 60), 'FPS no soportado; usar FPS entero')
    require(isinstance(plan['segments'], list) and 0 < len(plan['segments']) <= 100, 'Se requieren 1–100 segmentos')
    for segment in plan['segments']:
        keys(segment, ['in_seconds', 'out_seconds'] + (['zoom'] if version == 2 else []))
        if version == 2:
            require(number(segment['zoom']) and 1 <= segment['zoom'] <= 1.2, 'Zoom fuera de 1–1.2')
        start, end = segment['in_seconds'], segment['out_seconds']
        require(number(start) and number(end) and 0 <= start < end, 'Rango temporal inválido')
    if version == 2:
        from caption_style import validate_style
        validate_style(plan)
        if 'audio' in plan:
            from sound_edit import validate_audio
            duration = sum(frame(s['out_seconds'], tl['fps']) - frame(s['in_seconds'], tl['fps']) for s in plan['segments'])
            validate_audio(plan['audio'], path, tl['fps'], duration)
    return plan


def frame(seconds, fps):
    return int((Decimal(str(seconds)) * Decimal(str(fps))).quantize(Decimal('1'), rounding=ROUND_HALF_UP))


def source_ranges(plan, props):
    fps = float(props['FPS'])
    require(fps == plan['timeline']['fps'], 'Primera versión requiere FPS de fuente y timeline iguales')
    width, height = map(int, props['Resolution'].split('x'))
    require(height > width, 'La fuente debe ser vertical según Resolve')
    require(int(props.get('Audio Ch', '0')) > 0, 'Fuente sin audio')
    total = int(props['Frames'])
    ranges = []
    for segment in plan['segments']:
        require(segment['out_seconds'] <= total / fps, 'Segmento excede la duración de la fuente')
        start, end = (frame(segment[k], fps) for k in ('in_seconds', 'out_seconds'))
        require(0 <= start < end <= total, 'Rango de frames inválido')
        ranges.append((start, end))
    return ranges


def verify_timeline(timeline, ranges, allowed_audio_tracks=()):
    expected = [end - start for start, end in ranges]
    origin = timeline.GetStartFrame()
    for kind in ('video', 'audio'):
        require(timeline.GetTrackCount(kind) >= 1, 'Falta pista ' + kind)
        for index in range(2, timeline.GetTrackCount(kind) + 1):
            if kind == 'audio' and index in allowed_audio_tracks:
                continue
            require(not timeline.GetItemListInTrack(kind, index), 'Pista adicional con contenido: ' + kind)
        items = timeline.GetItemListInTrack(kind, 1) or []
        require(len(items) == len(ranges), 'Cantidad de clips incorrecta: ' + kind)
        position = origin
        for item, (start, _), duration in zip(items, ranges, expected):
            require(item.GetStart() == position and item.GetDuration() == duration and
                    item.GetLeftOffset() == start, 'Corte o posición incorrecta: ' + kind)
            position += duration
    require(timeline.GetEndFrame() - origin == sum(expected), 'Duración total incorrecta')
    return sum(expected)


def execute(plan, resolve, report, save, timeout):
    pm = resolve.GetProjectManager()
    # No abrir ni modificar proyectos existentes. CreateProject falla si hay colisión.
    name = plan['project_prefix'] + '_' + report['run_id']
    project = pm.CreateProject(name)
    require(project is not None, 'No se pudo crear proyecto nuevo (posible colisión)')
    report.update(project=name, stage='project_created')
    save()
    tl = plan['timeline']
    require(project.SetSettings({'timelineFrameRate': str(tl['fps']),
                                'timelineResolutionWidth': str(tl['width']),
                                'timelineResolutionHeight': str(tl['height'])}), 'No se pudieron fijar ajustes')
    pool = project.GetMediaPool()
    clips = pool.ImportMedia([plan['source']]) or []
    require(len(clips) == 1, 'Importación fallida')
    props = clips[0].GetClipProperty()
    ranges = source_ranges(plan, props)
    report.update(stage='source_validated', source={k: props[k] for k in ('FPS', 'Frames', 'Resolution', 'Audio Ch')}, ranges=ranges)
    save()
    sound_media = {}
    if 'audio' in plan:
        from sound_edit import import_sounds
        sound_media = import_sounds(pool, plan['audio'], tl['fps'])
    timeline = pool.CreateEmptyTimeline(tl['name'])
    require(timeline is not None and project.SetCurrentTimeline(timeline), 'No se pudo crear timeline')
    for start, end in ranges:
        require(pool.AppendToTimeline([{'mediaPoolItem': clips[0], 'startFrame': start,
                                       'endFrame': end}]), 'No se pudo añadir segmento')
    report['frames'] = verify_timeline(timeline, ranges)
    settings = timeline.GetSettings()
    for key, value in [('timelineFrameRate', tl['fps']), ('timelineResolutionWidth', tl['width']), ('timelineResolutionHeight', tl['height'])]:
        require(float(settings[key]) == value, 'Ajuste de timeline incorrecto: ' + key)
    require(pm.SaveProject(), 'No se pudo guardar proyecto')
    report.update(stage='timeline_verified', timeline=tl['name'])
    if 'audio' in plan:
        from sound_edit import apply_audio
        report['audio'] = apply_audio(project, timeline, plan['audio'], sound_media, tl['fps'])
        verify_timeline(timeline, ranges, [report['audio']['track']])
        report['stage'] = 'audio_verified'
        require(pm.SaveProject(), 'No se pudo guardar mezcla')
    save()
    if plan['schema_version'] == 2:
        from caption_style import apply_style, write_srt
        require(resolve.OpenPage('edit'), 'No se pudo abrir Edit para Fusion')
        report['style'] = apply_style(timeline, plan, Path(report['run_dir']))
        verify_timeline(timeline, ranges, [report['audio']['track']] if 'audio' in report else [])
        write_srt(plan['captions'], tl['fps'], Path(report['run_dir']) / 'captions.srt')
        report['stage'] = 'style_verified'
        require(pm.SaveProject(), 'No se pudo guardar estilo')
    save()
    export_draft(project, pm, plan, report, save, timeout)


def export_draft(project, pm, plan, report, save, timeout, wait=True):
    tl = plan['timeline']
    name = project.GetName()
    run_dir = Path(report['run_dir'])
    backup = run_dir / 'editable.drp'
    require(not backup.exists() and pm.ExportProject(name, str(backup), False), 'No se pudo exportar proyecto editable')
    require(backup.is_file() and backup.stat().st_size > 0, 'DRP ausente')
    report['editable_project'] = str(backup)
    require('H264' in project.GetRenderCodecs('mp4').values(), 'H.264 no disponible')
    require(project.SetCurrentRenderFormatAndCodec('mp4', 'H264'), 'Formato no disponible')
    require(project.SetCurrentRenderMode(1), 'No se pudo elegir single clip')
    render_settings = {'SelectAllFrames': True, 'TargetDir': str(run_dir),
        'CustomName': 'draft', 'ExportVideo': True, 'ExportAudio': True,
        'FormatWidth': tl['width'], 'FormatHeight': tl['height'], 'FrameRate': tl['fps'],
        'VideoQuality': 8000, 'AudioCodec': 'aac', 'AudioSampleRate': 48000}
    if 'color' in plan:
        render_settings.update(ColorSpaceTag='Rec.709', GammaTag='Gamma 2.4')
    require(project.SetRenderSettings(render_settings), 'Ajustes de render rechazados')
    job = project.AddRenderJob()
    require(bool(job), 'No se pudo crear trabajo de render')
    report.update(stage='render_queued', render_job=job)
    save()
    require(pm.SaveProject(), 'No se pudo guardar trabajo antes de renderizar')
    require(project.StartRendering([job]), 'No se pudo iniciar render')
    if not wait:
        report['stage'] = 'render_started'
        save()
        return
    deadline = time.monotonic() + timeout
    while True:
        status = project.GetRenderJobStatus(job)
        report['render_status'] = status
        save()
        if status.get('JobStatus') == 'Complete':
            break
        require(status.get('JobStatus') not in ('Failed', 'Cancelled', 'Background Render Cancelled', 'Remote Render Cancelled'), 'Render fallido: ' + str(status))
        if time.monotonic() >= deadline:
            # Se conserva el trabajo y su ID; no cancelar otros procesos ni reintentar.
            raise ValueError('Tiempo agotado; consultar trabajo guardado antes de reintentar')
        time.sleep(1)
    draft = run_dir / 'draft.mp4'
    require(draft.is_file() and draft.stat().st_size > 0, 'Render completo pero archivo ausente')
    require(pm.SaveProject(), 'No se pudo guardar al finalizar')
    report.update(stage='complete', draft=str(draft), editable_project=str(backup), draft_bytes=draft.stat().st_size)
    save()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('plan', type=Path)
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--worker', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--render-timeout', type=int, default=300)
    args = parser.parse_args()
    try:
        require(1 <= args.render_timeout <= 3600, 'Timeout fuera de 1–3600 segundos')
        path = args.plan.resolve()
        plan = load_plan(path)
        if not args.execute:
            print(json.dumps({'status': 'valid', 'scope': 'estructura y archivos; metadatos y rangos se comprueban en Resolve antes de crear timeline'}, ensure_ascii=True))
            return 0
        require(plan['schema_version'] != 3, 'Los planes multi-fuente se ejecutan por etapas mediante MCP')
        require('audio' not in plan, 'La ruta nativa con SFX sigue bloqueada tras cierres Qt observados; usar sound_edit y export_draft mediante MCP')
        if not args.worker:
            diagnostic = diagnose(APP, 30)
            require(diagnostic['status'] == 'ok', 'Diagnóstico: ' + diagnostic['status'])
            try:
                return subprocess.run([str(APP / 'Contents/Applications/ResolvePython'), str(Path(__file__).resolve()),
                                       str(path), '--execute', '--worker', '--render-timeout', str(args.render_timeout)],
                                      check=False, timeout=args.render_timeout + 120).returncode
            except subprocess.TimeoutExpired:
                raise ValueError('Worker sin respuesta: comprobar Resolve e informe antes de reintentar')
        import DaVinciResolveScript as api
        resolve = api.scriptapp('Resolve')
        require(resolve is not None, 'Resolve inaccesible')
        import uuid
        run_id = time.strftime('%Y%m%d_%H%M%S') + '_' + uuid.uuid4().hex[:8]
        run_dir = Path(plan['output_dir']) / run_id
        run_dir.mkdir(parents=True, exist_ok=False)
        report = {'schema_version': 1, 'run_id': run_id, 'run_dir': str(run_dir), 'stage': 'validated',
                  'plan_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'resolve_version': resolve.GetVersionString()}
        def save():
            temporary = run_dir / 'result.tmp'
            temporary.write_text(json.dumps(report, indent=2, ensure_ascii=True), encoding='utf-8')
            temporary.replace(run_dir / 'result.json')
        (run_dir / 'plan.json').write_text(json.dumps(plan, indent=2, ensure_ascii=True), encoding='utf-8')
        started = time.monotonic()
        try:
            execute(plan, resolve, report, save, args.render_timeout)
        except Exception as exc:
            report.update(status='failed', error=str(exc))
            raise
        finally:
            report['elapsed_seconds'] = round(time.monotonic() - started, 3)
            save()
            print(json.dumps(report, ensure_ascii=True))
        return 0
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(json.dumps({'status': 'failed', 'error': str(exc)}, ensure_ascii=True), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
