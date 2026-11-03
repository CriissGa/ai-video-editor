#!/usr/bin/env python3
"""Catalogar sonidos locales en PCM estéreo con caché y regiones activas sugeridas."""
import argparse
import array
import json
import math
from pathlib import Path
import subprocess
import sys
import wave

from edit_video import require
from transcribe_video import file_hash


def analyze(path):
    with wave.open(str(path), 'rb') as source:
        channels, rate, count = source.getnchannels(), source.getframerate(), source.getnframes()
        require(source.getsampwidth() == 2 and channels in (1, 2) and rate == 48000 and count <= rate * 60,
                'PCM debe ser mono/estéreo 16-bit/48 kHz, máximo 60 segundos')
        samples = array.array('h', source.readframes(count))
    if sys.byteorder != 'little':
        samples.byteswap()
    window = rate // 100 * channels
    levels = []
    for index in range(0, len(samples), window):
        chunk = samples[index:index + window]
        levels.append(math.sqrt(sum(v*v for v in chunk) / max(1, len(chunk))) / 32768)
    peak = max((abs(v) for v in samples), default=0) / 32768
    gate = max(0.002, max(levels, default=0) * 0.08)
    active = [index for index, value in enumerate(levels) if value >= gate]
    runs = []
    for index in active:
        if not runs or index - runs[-1][1] > 8:
            runs.append([index, index])
        else:
            runs[-1][1] = index
    regions = [{'in_seconds': max(0, (a - 2) / 100), 'out_seconds': min(count / rate, (b + 4) / 100)}
               for a, b in runs if b - a >= 2]
    return {'duration_seconds': count / rate, 'sample_peak_dbfs': round(20 * math.log10(max(peak, 1e-10)), 2),
            'regions': regions}



def pcm_peak(path):
    """Pico de muestras en streaming; no es true peak ni loudness perceptual."""
    peak = 0
    with wave.open(str(path), 'rb') as source:
        require(source.getsampwidth() == 2, 'Se requiere PCM16')
        duration = source.getnframes() / source.getframerate()
        while True:
            chunk = source.readframes(65536)
            if not chunk:
                break
            samples = array.array('h', chunk)
            if sys.byteorder != 'little':
                samples.byteswap()
            peak = max(peak, max((abs(v) for v in samples), default=0))
    return {'duration_seconds': duration, 'sample_peak_dbfs': round(20 * math.log10(max(peak / 32768, 1e-10)), 2)}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folder', type=Path)
    parser.add_argument('--channels', type=int, choices=[1,2], default=2)
    parser.add_argument('--output-dir', type=Path, default=Path('outputs/sounds'))
    args = parser.parse_args()
    try:
        require(args.folder.is_dir(), 'Carpeta de sonidos ausente')
        args.output_dir.mkdir(parents=True, exist_ok=True)
        catalog = []
        for source in sorted(args.folder.iterdir()):
            if not source.is_file() or source.suffix.lower() not in ('.mp3', '.wav', '.m4a', '.aiff'):
                continue
            digest = file_hash(source)
            destination = args.output_dir.resolve() / (digest + ('-mono' if args.channels == 1 else '') + '.wav')
            if not destination.exists():
                temporary = destination.with_suffix('.tmp.wav')
                subprocess.run(['/usr/bin/afconvert', '-f', 'WAVE', '-d', 'LEI16@48000', '-c', str(args.channels),
                                str(source.resolve()), str(temporary)], check=True, capture_output=True, timeout=60)
                temporary.replace(destination)
            catalog.append({'source': str(source.resolve()), 'sha256': digest, 'pcm': str(destination), **analyze(destination)})
        require(bool(catalog), 'No se encontraron sonidos compatibles')
        path = args.output_dir / ('catalog-mono.json' if args.channels == 1 else 'catalog.json')
        path.write_text(json.dumps({'schema_version': 1, 'converter': 'afconvert PCM16 %d channels 48000' % args.channels, 'sounds': catalog}, indent=2), encoding='utf-8')
        print(json.dumps({'status': 'complete', 'catalog': str(path.resolve()), 'sounds': len(catalog)}))
        return 0
    except (ValueError, OSError, subprocess.SubprocessError, wave.Error) as exc:
        print(json.dumps({'status': 'failed', 'error': str(exc)}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
