#!/usr/bin/env python3
"""Transcripción local de Resolve con caché por contenido, versión y configuración."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parent))
from edit_video import APP, require
from diagnose_resolve import diagnose


def file_hash(path):
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def timecode_frame(value, fps):
    parts = value.split(':')
    require(len(parts) == 4 and all(p.isdigit() for p in parts), 'Timecode no soportado')
    hours, minutes, seconds, frames = map(int, parts)
    require(minutes < 60 and seconds < 60 and frames < fps, 'Timecode inválido')
    return ((hours * 60 + minutes) * 60 + seconds) * fps + frames


def normalize(raw, props):
    fps = float(props['FPS'])
    require(fps.is_integer(), 'Transcripción v1 requiere FPS entero')
    fps = int(fps)
    origin = timecode_frame(props['Start TC'], fps)
    total = int(props['Frames'])
    words = []
    for segment in raw.get('segments', []):
        for word in segment.get('words', []):
            text = word['text'].strip()
            if not text or text == '(...)':
                continue
            start = timecode_frame(word['start'], fps) - origin
            end = timecode_frame(word['end'], fps) - origin
            require(0 <= start <= end <= total, 'Palabra fuera de la fuente')
            words.append({'start_frame': start, 'end_frame': end, 'text': text})
    require(bool(words), 'Resolve no devolvió palabras con tiempos')
    return words


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--cache-dir', type=Path, default=Path('transcripts'))
    parser.add_argument('--language', choices=['auto', 'Spanish', 'English'], default='auto')
    parser.add_argument('--project', help='Reutilizar solo un proyecto AIEditor_Test_Transcript_ del mismo medio')
    parser.add_argument('--timeout', type=int, default=600)
    parser.add_argument('--worker', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()
    try:
        source = args.source.resolve()
        require(source.is_file() and source.stat().st_size > 0, 'Fuente ausente o vacía')
        require(1 <= args.timeout <= 3600, 'Timeout fuera de 1–3600 segundos')
        if not args.worker:
            require(diagnose(APP, 30)['status'] == 'ok', 'Diagnóstico de Resolve falló')
            return subprocess.run([str(APP / 'Contents/Applications/ResolvePython'), str(Path(__file__).resolve()),
                str(source), '--cache-dir', str(args.cache_dir.resolve()), '--language', args.language,
                '--timeout', str(args.timeout), '--worker'] + (['--project', args.project] if args.project else []), check=False).returncode
        import DaVinciResolveScript as api
        resolve = api.scriptapp('Resolve')
        require(resolve is not None, 'Resolve inaccesible')
        config = {'schema_version': 1, 'engine': 'resolve', 'engine_version': resolve.GetVersionString(),
                  'language': args.language, 'speaker_detection': False, 'source_sha256': file_hash(source)}
        key = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()
        args.cache_dir.mkdir(parents=True, exist_ok=True)
        target = args.cache_dir / (key + '.json')
        if target.exists():
            cached = json.loads(target.read_text(encoding='utf-8'))
            require(cached.get('config') == config and bool(cached.get('words')), 'Caché inválida')
            print(json.dumps({'status': 'cached', 'transcript': str(target), 'words': len(cached['words'])}))
            return 0
        pm = resolve.GetProjectManager()
        require(not args.project or args.project.startswith('AIEditor_Test_Transcript_'), 'Solo se permiten proyectos de transcripción de prueba')
        current = pm.GetCurrentProject()
        project = ((current if current and current.GetName() == args.project else pm.LoadProject(args.project))
                   if args.project else pm.CreateProject('AIEditor_Test_Transcript_' + uuid.uuid4().hex[:12]))
        require(project is not None, 'No se pudo crear proyecto de prueba')
        if args.project:
            require(project.GetSettings().get('transcriptionLanguage') == args.language, 'El idioma del proyecto no coincide')
        else:
            require(project.SetSettings({'transcriptionLanguage': args.language}), 'Idioma rechazado')
        clips = ([c for c in project.GetMediaPool().GetRootFolder().GetClipList() if c.GetClipProperty('File Path') == str(source)] if args.project else project.GetMediaPool().ImportMedia([str(source)])) or []
        require(len(clips) == 1, 'Importación fallida')
        clip = clips[0]
        props = clip.GetClipProperty()
        require(float(props['FPS']).is_integer(), 'FPS fraccional no soportado')
        started = time.monotonic()
        # La página Deliver rechaza TranscribeAudio y devuelve Inactive en esta instalación.
        require(resolve.OpenPage('edit'), 'No se pudo abrir la página Edit mediante API')
        existing_raw = clip.GetTranscription()
        if not existing_raw and project.GetTranscribeAudioStatus().get('JobStatus') not in ('Initializing', 'Analyzing'):
            require(clip.TranscribeAudio(False), 'Transcripción rechazada')
        deadline = started + args.timeout
        while not existing_raw:
            status = project.GetTranscribeAudioStatus()
            if status.get('JobStatus') == 'Complete':
                break
            require(status.get('JobStatus') not in ('Cancelled', 'Failed') and not status.get('Error'), 'Transcripción fallida: ' + str(status))
            require(time.monotonic() < deadline, 'Tiempo agotado: comprobar proyecto ' + project.GetName())
            time.sleep(1)
        raw = existing_raw or clip.GetTranscription()
        words = normalize(raw, props)
        payload = {'config': config, 'project': project.GetName(), 'source': str(source),
                   'fps': float(props['FPS']), 'source_frames': int(props['Frames']),
                   'language': raw.get('language'), 'words': words, 'raw': raw,
                   'elapsed_seconds': round(time.monotonic() - started, 3)}
        require(pm.SaveProject(), 'No se pudo guardar proyecto de transcripción')
        temporary = target.with_suffix('.' + uuid.uuid4().hex + '.tmp')
        temporary.write_text(json.dumps(payload, indent=2), encoding='utf-8')
        temporary.replace(target)
        print(json.dumps({'status': 'complete', 'transcript': str(target), 'words': len(words), 'elapsed_seconds': payload['elapsed_seconds']}))
        return 0
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(json.dumps({'status': 'failed', 'error': str(exc)}), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
