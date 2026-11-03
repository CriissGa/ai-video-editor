#!/usr/bin/env python3
"""Proyecta palabras de una transcripción cacheada al montaje y crea un plan v2."""
import argparse
import json
from pathlib import Path
import re
import textwrap

from edit_video import frame, load_plan, require
from transcribe_video import file_hash
from caption_style import PRESET, PRESETS


def generate_captions(plan, transcript, preset=PRESET):
    width = min(22, PRESETS[preset]['line_width'])
    fps = plan['timeline']['fps']
    require(transcript['fps'] == fps, 'FPS de transcripción distinto')
    captions = []
    offset = 0
    for segment in plan['segments']:
        start, end = (frame(segment[k], fps) for k in ('in_seconds', 'out_seconds'))
        require(end <= transcript['source_frames'], 'Segmento fuera de transcripción')
        words = [w for w in transcript['words'] if start <= w['start_frame'] < end]
        group = []
        groups = []
        for word in words:
            text = ' '.join(w['text'] for w in group + [word]).upper()
            lines = textwrap.wrap(text, width=width, break_long_words=False, break_on_hyphens=False)
            if group and (len(group) >= 4 or len(lines) > 2 or len(text) > 42 or
                          word['start_frame'] - group[-1]['end_frame'] > fps * 0.5):
                groups.append(group)
                group = []
            group.append(word)
            if re.search(r'[.!?]$', word['text']):
                groups.append(group)
                group = []
        if group:
            groups.append(group)
        for index, group in enumerate(groups):
            a = offset + group[0]['start_frame'] - start
            next_start = groups[index + 1][0]['start_frame'] if index + 1 < len(groups) else end
            b = offset + min(end, next_start, max(group[-1]['end_frame'], group[0]['start_frame'] + 12)) - start
            if a >= b:
                continue
            text = ' '.join(w['text'] for w in group).upper()
            emphasis = any(token in text for token in ('PROFESSIONAL', 'FIRST TIME', 'MYSELF', 'CLASS', 'MY BEST', 'PAINT MY HAIR'))
            captions.append({'in_seconds': a / fps, 'out_seconds': b / fps,
                             'text': '\n'.join(textwrap.wrap(text, width=width, break_long_words=False, break_on_hyphens=False)),
                             'emphasis': emphasis})
        offset += end - start
    return captions


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('plan', type=Path)
    parser.add_argument('transcript', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--zooms', nargs='+', type=float)
    parser.add_argument('--preset', choices=sorted(PRESETS), default=PRESET)
    args = parser.parse_args()
    try:
        plan = load_plan(args.plan.resolve())
        require(plan['schema_version'] == 1, 'Entrada debe ser un plan v1')
        transcript = json.loads(args.transcript.read_text(encoding='utf-8'))
        require(transcript['config']['source_sha256'] == file_hash(Path(plan['source'])), 'Transcripción corresponde a otro contenido')
        zooms = args.zooms or [1.0] * len(plan['segments'])
        require(len(zooms) == len(plan['segments']), 'Se requiere un zoom por segmento')
        plan['captions'] = generate_captions(plan, transcript, args.preset)
        plan.update(schema_version=2, style={'preset': args.preset})
        for segment, zoom in zip(plan['segments'], zooms):
            segment['zoom'] = zoom
        from caption_style import validate_style
        require(all(1 <= z <= 1.2 for z in zooms), 'Zoom fuera de 1–1.2')
        validate_style(plan)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x', encoding='utf-8') as target:
            json.dump(plan, target, indent=2, ensure_ascii=False)
        print(json.dumps({'status': 'complete', 'plan': str(args.output.resolve()), 'captions': len(plan['captions'])}))
        return 0
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(json.dumps({'status': 'failed', 'error': str(exc)}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
