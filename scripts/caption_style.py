"""Preset de subtítulos Text+ editables y zoom por segmento en Fusion."""
from edit_video import frame, keys, number, require

PRESET = 'bold-yellow-v1'
PRESETS = {PRESET: {'size': 0.075, 'outline': 0.035, 'shadow': False, 'line_width': 24},
           'bold-yellow-v2': {'size': 0.10, 'outline': 0.05, 'shadow': True, 'line_width': 18},
           'bold-party-v3': {'size': 0.105, 'emphasis_size': 0.14, 'outline': 0.075, 'shadow': True, 'line_width': 16,
                             'focus_words': ['PROFESSIONAL', 'PROFESIONAL', 'MYSELF', 'SOLO', 'BEST', 'MEJOR', 'CLASS', 'CLASE', 'HAIR', 'PELO']}}


def validate_style(plan):
    keys(plan['style'], ['preset'] + (['events'] if 'events' in plan['style'] else []))
    require(plan['style']['preset'] in PRESETS, 'Preset desconocido')
    preset = PRESETS[plan['style']['preset']]
    fps = plan['timeline']['fps']
    duration = sum(frame(s['out_seconds'], fps) - frame(s['in_seconds'], fps) for s in plan['segments'])
    from edit_effects import validate_events
    validate_events(plan['style'].get('events', []), fps, duration)
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
                len(text.splitlines()) <= 2 and all(len(line) <= preset['line_width'] for line in text.splitlines()),
                'Subtítulo excede dos líneas o el ancho admitido por el preset')
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
    preset = PRESETS[plan['style']['preset']]
    events = plan['style'].get('events', [])
    effect_checks = []
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
        if events:
            from edit_effects import apply_effects
            checked = apply_effects(transform, events, fps, offset, duration, local_start, segment['zoom'])
            effect_checks.append({'segment': index + 1, 'samples': checked})
        background = transform
        captions = caption_intersections(plan['captions'], fps, offset, duration)
        for caption, start, end in captions:
            count += 1
            text = comp.AddTool('TextPlus')
            text.SetAttrs({'TOOLS_Name': 'Caption_%03d' % count})
            text_size = preset.get('emphasis_size', preset['size']) if caption['emphasis'] else preset['size']
            for key, value in {'StyledText': caption['text'], 'Font': 'Arial', 'Style': 'Bold',
                'Size': text_size, 'Center': {1: 0.5, 2: 0.25}, 'Red1': 1.0,
                'Green1': 0.85 if caption['emphasis'] else 1.0,
                'Blue1': 0.12 if caption['emphasis'] else 1.0,
                'Enabled2': 1, 'SelectElement': 1, 'ElementShape2': 1, 'Thickness2': preset['outline'],
                'Red2': 0, 'Green2': 0, 'Blue2': 0, 'Alpha2': 1}.items():
                text.SetInput(key, value)
            if preset['shadow']:
                for key, value in {'Enabled3': 1, 'SelectElement': 2, 'ElementShape3': 0,
                    'Red3': 0, 'Green3': 0, 'Blue3': 0, 'Alpha3': 0.5,
                    'Offset3': {1: 0.025, 2: -0.025}, 'SoftnessX3': 0.012, 'SoftnessY3': 0.012}.items():
                    text.SetInput(key, value)
            require(text.GetInput('Size') == text_size and text.GetInput('Thickness2') == preset['outline'], 'Tamaño o borde no aplicado')
            if preset['shadow']:
                require(text.GetInput('Enabled3') == 1 and text.GetInput('Alpha3') == 0.5, 'Sombra no aplicada')
            require(text.GetInput('StyledText') == caption['text'], 'Texto no aplicado')
            merge = comp.AddTool('Merge')
            merge.SetAttrs({'TOOLS_Name': 'CaptionGate_%03d' % count})
            require(merge.ConnectInput('Background', background) and merge.ConnectInput('Foreground', text), 'Conexión de subtítulo fallida')
            begin, finish = local_start + start, local_start + end
            merge.Blend.SetExpression('iif(time >= %d and time < %d, 1, 0)' % (begin, finish))
            require(merge.GetInput('Blend', begin) == 1 and merge.GetInput('Blend', finish) == 0,
                    'Temporización de subtítulo incorrecta')
            if 'emphasis_size' in preset and caption['emphasis']:
                text.Size.SetExpression('%.8f*(1+iif(time >= %d and time < %d, 0.12*sin((time-%d)/6*3.14159265), 0))' % (text_size, begin, begin+6, begin))
                require(text.GetInput('Size', begin+3) > text_size, 'Pop de palabra no aplicado')
            background = merge
        require(media_out.ConnectInput('Input', background), 'No se pudo conectar salida Fusion')
        if captions and 'emphasis_size' not in preset:
            _, start, end = captions[min(1, len(captions)-1)]
            path = run_dir / ('preview-%02d.png' % (index + 1))
            exported = item.ExportFrame((start + end) // 2, {'outputType': 'file', 'filePath': str(path), 'maxDimension': 960})
            require(exported.get('success') and path.is_file(), 'No se pudo exportar fotograma de revisión')
            previews.append(str(path))
        offset += duration
    return {'preset': plan['style']['preset'], 'caption_nodes': count, 'previews': previews, 'effect_checks': effect_checks}


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
