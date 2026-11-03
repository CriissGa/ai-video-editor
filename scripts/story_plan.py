"""Plan v3 multi-fuente y montaje por etapas mediante MCP."""
import copy
from pathlib import Path
import re

from edit_video import frame, keys, require, number, validate_plan, source_ranges, verify_timeline


def validate_story(plan, path):
    keys(plan, ['schema_version', 'sources', 'project_prefix', 'timeline', 'segments', 'captions', 'style', 'color', 'output_dir'] + (['audio'] if 'audio' in plan else []))
    require(isinstance(plan['sources'], dict) and 1 <= len(plan['sources']) <= 10, 'Se requieren 1–10 fuentes')
    for name, source in plan['sources'].items():
        require(re.fullmatch(r'[A-Za-z0-9_-]{1,40}', name) and isinstance(source, str), 'Fuente inválida')
    require(isinstance(plan['segments'], list) and 0 < len(plan['segments']) <= 100, 'Segmentos inválidos')
    for segment in plan['segments']:
        keys(segment, ['source', 'in_seconds', 'out_seconds', 'zoom', 'zoom_end'])
        require(isinstance(segment['source'], str) and segment['source'] in plan['sources'], 'Referencia de fuente desconocida')
        require(number(segment['zoom_end']) and 1 <= segment['zoom_end'] <= 1.2, 'Zoom final fuera de 1–1.2')
    from color_pipeline import validate_color
    validate_color(plan['color'])
    base = copy.deepcopy(plan)
    base['schema_version'] = 2
    base.pop('sources')
    base.pop('color')
    for segment in base['segments']:
        segment.pop('source')
        segment.pop('zoom_end')
    for name, source in plan['sources'].items():
        candidate = copy.deepcopy(base)
        candidate['source'] = source
        checked = validate_plan(candidate, path)
        plan['sources'][name] = checked['source']
    # Compartir validación de parámetros y rutas de audio sin duplicarla.
    plan['output_dir'] = checked['output_dir']
    if 'audio' in plan:
        plan['audio'] = checked['audio']
    return plan


def story_ranges(plan, media):
    ranges = []
    for segment in plan['segments']:
        source = segment['source']
        mini = {'timeline': plan['timeline'], 'segments': [segment]}
        ranges.append(source_ranges(mini, media[source].GetClipProperty())[0])
    return ranges


def verify_story(timeline, plan, ranges, allowed_audio_tracks=()):
    total = verify_timeline(timeline, ranges, allowed_audio_tracks)
    for kind in ('video', 'audio'):
        for item, segment in zip(timeline.GetItemListInTrack(kind, 1), plan['segments']):
            require(Path(item.GetMediaPoolItem().GetClipProperty('File Path')).resolve() == Path(plan['sources'][segment['source']]), 'Clip pertenece a otra fuente')
    return total


def create_story_project(plan, resolve, project_name):
    require(project_name.startswith(plan['project_prefix'] + '_'), 'Nombre de proyecto fuera del prefijo de prueba')
    pm = resolve.GetProjectManager()
    project = pm.CreateProject(project_name)
    require(project is not None, 'Proyecto ya existe o no se pudo crear')
    tl = plan['timeline']
    require(project.SetSettings({'timelineFrameRate':str(tl['fps']), 'timelineResolutionWidth':str(tl['width']), 'timelineResolutionHeight':str(tl['height'])}), 'Ajustes de timeline rechazados')
    from color_pipeline import apply_color_settings, verify_hlg_sources
    color = apply_color_settings(project, plan['color'])
    pool = project.GetMediaPool()
    clips = pool.ImportMedia(list(plan['sources'].values())) or []
    require(len(clips) == len(plan['sources']), 'Importación multi-fuente incompleta')
    by_path = {c.GetClipProperty('File Path'):c for c in clips}
    media = {name: by_path[path] for name,path in plan['sources'].items()}
    color['sources'] = verify_hlg_sources(media)
    ranges = story_ranges(plan, media)
    timeline = pool.CreateEmptyTimeline(tl['name'])
    require(timeline is not None and project.SetCurrentTimeline(timeline), 'Timeline no creada')
    for segment, (start, end) in zip(plan['segments'], ranges):
        require(pool.AppendToTimeline([{'mediaPoolItem':media[segment['source']], 'startFrame':start, 'endFrame':end}]), 'No se pudo montar segmento')
    total = verify_story(timeline, plan, ranges)
    require(pm.SaveProject(), 'No se pudo guardar montaje multi-fuente')
    return project, {'stage':'story_verified', 'project':project_name, 'timeline':tl['name'], 'frames':total, 'ranges':ranges, 'color':color}
