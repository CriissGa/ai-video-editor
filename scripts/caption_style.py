"""Preset de subtítulos Text+ editables y zoom por segmento en Fusion."""
from edit_video import frame, keys, number, require

PRESET = 'bold-yellow-v1'


def validate_style(plan):
    keys(plan['style'], ['preset'])
    require(plan['style']['preset'] == PRESET, 'Preset desconocido')
    fps = plan['timeline']['fps']
    duration = sum(frame(s['out_seconds'], fps) - frame(s['in_seconds'], fps) for s in plan['segments'])
    require(isinstance(plan['captions'], list) and 0 < len(plan['captions']) <= 500, 'Se requieren 1–500 subtítulos')
    previous_end = 0
    for caption in plan['captions']:
        keys(caption, ['in_seconds', 'out_seconds', 'text', 'emphasis'])
        start, end = caption['in_seconds'], caption['out_seconds']
        require(number(start) and number(end), 'Tiempo de subtítulo inválido')
        start, end = frame(start, fps), frame(end, fps)
        require(0 <= previous_end <= start < end <= duration, 'Subtítulos superpuestos o fuera de timeline')
        previous_end = end
        text = caption['text']
        require(isinstance(text, str) and bool(text.strip()) and len(text) <= 44 and
                len(text.splitlines()) <= 2 and all(len(line) <= 24 for line in text.splitlines()),
                'Subtítulo debe tener máximo dos líneas de 24 caracteres, 44 en total')
        require(type(caption['emphasis']) is bool, 'Énfasis debe ser booleano')


def caption_intersections(captions, fps, offset, duration):
    result = []
    for caption in captions:
        start = max(0, frame(caption['in_seconds'], fps) - offset)
        end = min(duration, frame(caption['out_seconds'], fps) - offset)
        if start < end:
            result.append((caption, start, end))
    return result


def apply_style(timeline, plan, run_dir):
    fps = plan['timeline']['fps']
    offset = 0
    count = 0
    previews = []
    for index, (item, segment) in enumerate(zip(timeline.GetItemListInTrack('video', 1), plan['segments'])):
        comp = item.AddFusionComp()
        require(comp is not None, 'No se pudo crear composición Fusion')
        media_in = comp.FindToolByID('MediaIn')
        media_out = comp.FindToolByID('MediaOut')
        require(media_in is not None and media_out is not None, 'Faltan nodos de medios')
        # Los tiempos de Fusion son locales al clip; comprobar antes de asignarlos.
        local_start = int(comp.GetAttrs()['COMPN_RenderStart'])
        duration = int(item.GetDuration())
        transform = comp.AddTool('Transform')
        transform.SetAttrs({'TOOLS_Name': 'AIEditor_Zoom'})
        require(transform.ConnectInput('Input', media_in), 'No se pudo conectar zoom')
        transform.SetInput('Size', segment['zoom'])
        require(abs(transform.GetInput('Size') - segment['zoom']) < 0.0001, 'Zoom no aplicado')
        background = transform
        captions = caption_intersections(plan['captions'], fps, offset, duration)
        for caption, start, end in captions:
            count += 1
            text = comp.AddTool('TextPlus')
            text.SetAttrs({'TOOLS_Name': 'Caption_%03d' % count})
            for key, value in {'StyledText': caption['text'], 'Font': 'Arial', 'Style': 'Bold',
                'Size': 0.075, 'Center': {1: 0.5, 2: 0.25}, 'Red1': 1.0,
                'Green1': 0.85 if caption['emphasis'] else 1.0,
                'Blue1': 0.12 if caption['emphasis'] else 1.0,
                'Enabled2': 1, 'SelectElement': 1, 'ElementShape2': 1, 'Thickness2': 0.035,
                'Red2': 0, 'Green2': 0, 'Blue2': 0, 'Alpha2': 1}.items():
                text.SetInput(key, value)
            require(text.GetInput('StyledText') == caption['text'], 'Texto no aplicado')
            merge = comp.AddTool('Merge')
            merge.SetAttrs({'TOOLS_Name': 'CaptionGate_%03d' % count})
            require(merge.ConnectInput('Background', background) and merge.ConnectInput('Foreground', text), 'Conexión de subtítulo fallida')
            begin, finish = local_start + start, local_start + end
            merge.Blend.SetExpression('iif(time >= %d and time < %d, 1, 0)' % (begin, finish))
            require(merge.GetInput('Blend', begin) == 1 and merge.GetInput('Blend', finish) == 0,
                    'Temporización de subtítulo incorrecta')
            background = merge
        require(media_out.ConnectInput('Input', background), 'No se pudo conectar salida Fusion')
        if captions:
            _, start, end = captions[min(1, len(captions)-1)]
            path = run_dir / ('preview-%02d.png' % (index + 1))
            exported = item.ExportFrame((start + end) // 2, {'outputType': 'file', 'filePath': str(path), 'maxDimension': 960})
            require(exported.get('success') and path.is_file(), 'No se pudo exportar fotograma de revisión')
            previews.append(str(path))
        offset += duration
    return {'preset': PRESET, 'caption_nodes': count, 'previews': previews}


def write_srt(captions, fps, path):
    def stamp(seconds):
        milliseconds = round(frame(seconds, fps) * 1000 / fps)
        seconds, ms = divmod(milliseconds, 1000)
        minutes, sec = divmod(seconds, 60)
        hours, minute = divmod(minutes, 60)
        return '%02d:%02d:%02d,%03d' % (hours, minute, sec, ms)
    blocks = ['%d\n%s --> %s\n%s' % (index, stamp(c['in_seconds']), stamp(c['out_seconds']), c['text'])
              for index, c in enumerate(captions, 1)]
    path.write_text('\n\n'.join(blocks) + '\n', encoding='utf-8')
