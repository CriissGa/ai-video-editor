"""Eventos de zoom y temblor: tiempos de timeline, expresiones Fusion verificables."""
from edit_video import frame, keys, number, require


def validate_events(events, fps, duration):
    require(isinstance(events, list) and len(events) <= 40, 'Máximo 40 eventos')
    by_type = {'punch_zoom': [], 'shake': [], 'whip': []}
    for event in events:
        keys(event, ['type', 'in_seconds', 'out_seconds', 'amount'])
        kind = event['type']
        require(isinstance(kind, str) and kind in by_type, 'Tipo de efecto desconocido')
        start, end, amount = event['in_seconds'], event['out_seconds'], event['amount']
        require(number(start) and number(end) and number(amount), 'Parámetro de efecto inválido')
        require(0 <= start < end <= duration / fps, 'Tiempo de efecto fuera de timeline')
        start, end = frame(start, fps), frame(end, fps)
        require(0 <= start < end <= duration, 'Efecto fuera de timeline')
        if kind == 'punch_zoom':
            require(1.05 <= amount <= 1.35 and 4 <= end - start <= fps * 3, 'Zoom debe ser 1.05–1.35 durante 4 frames–3 s')
        elif kind == 'shake':
            require(0.001 <= amount <= 0.015 and 3 <= end - start <= fps * 0.6, 'Temblor debe ser 0.001–0.015 durante 3 frames–0.6 s')
        else:
            require(0.015 <= abs(amount) <= 0.06 and 3 <= end-start <= 8, 'Barrido fuera de límites')
        by_type[kind].append((start, end))
    for intervals in by_type.values():
        ordered = sorted(intervals)
        require(all(a[1] <= b[0] for a, b in zip(ordered, ordered[1:])), 'No superponer efectos del mismo tipo')


def effect_expressions(events, fps, offset, duration, local_start, base_zoom):
    zoom_terms, x_terms, y_terms = [str(base_zoom)], ['0.5'], ['0.5']
    samples = []
    for event in events:
        start = frame(event['in_seconds'], fps) - offset + local_start
        end = frame(event['out_seconds'], fps) - offset + local_start
        if start >= local_start + duration or end <= local_start:
            continue
        ramp = 'iif(time >= %d and time < %d, min(1, max(0, (time-(%d)+1)/3), max(0, (%d-time)/4)), 0)' % (start, end, start, end)
        if event['type'] == 'punch_zoom':
            zoom_terms.append('(1 + %.8f*(%s))' % (event['amount'] - 1, ramp))
        elif event['type'] == 'shake':
            # El leve sobreescaneo evita bordes negros durante el desplazamiento.
            zoom_terms.append('(1 + 0.04*(%s))' % ramp)
            x_terms.append('%.8f*sin((time-(%d))*2.4)*(%s)' % (event['amount'], start, ramp))
            y_terms.append('%.8f*sin((time-(%d))*3.1)*(%s)' % (event['amount'] * 0.65, start, ramp))
        else:
            envelope = 'iif(time >= %d and time < %d, 1-(time-(%d))/%d, 0)' % (start,end,start,end-start)
            zoom_terms.append('(1+0.18*(%s))' % envelope)
            x_terms.append('%.8f*(%s)' % (event['amount'],envelope))
        sample = max(local_start, min(local_start + duration - 1, (start + end) // 2))
        samples.append({'type': event['type'], 'frame': sample})
    return '*'.join(zoom_terms), 'Point(%s, %s)' % ('+'.join(x_terms), '+'.join(y_terms)), samples


def apply_effects(transform, events, fps, offset, duration, local_start, base_zoom):
    zoom, center, samples = effect_expressions(events, fps, offset, duration, local_start, base_zoom)
    transform.Size.SetExpression(zoom)
    transform.Center.SetExpression(center)
    measured = []
    for sample in samples:
        at = sample['frame']
        size = transform.GetInput('Size', at)
        point = transform.GetInput('Center', at)
        require(size > base_zoom, 'Efecto sin aumento de escala')
        if sample['type'] in ('shake','whip'):
            require(abs(point[1] - 0.5) + abs(point[2] - 0.5) > 0.00001, 'Temblor sin desplazamiento')
        measured.append(dict(sample, size=size, center=point))
    return measured


def whip_blur_expression(events,fps,offset,duration,local_start):
    terms=[]
    for event in events:
        if event['type']!='whip':continue
        a=frame(event['in_seconds'],fps)-offset+local_start
        b=frame(event['out_seconds'],fps)-offset+local_start
        if a>=local_start+duration or b<=local_start:continue
        terms.append('iif(time >= %d and time < %d, 10*(1-(time-(%d))/%d), 0)'%(a,b,a,b-a))
    return '+'.join(terms) if terms else '0'
